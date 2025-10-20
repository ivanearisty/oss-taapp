"""End-to-end tests for the mail service."""

import os
import socket
import subprocess
import time
from contextlib import closing
from enum import IntEnum
from pathlib import Path

import pytest


class HTTPStatus(IntEnum):
    """HTTP status codes used in the API."""

    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500


def _free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _wait_for_ready(base_url: str, timeout_s: int = 45) -> None:
    import httpx

    start = time.time()
    while time.time() - start < timeout_s:
        try:
            r = httpx.get(f"{base_url}/openapi.json", timeout=2.0)
            if r.status_code < HTTPStatus.INTERNAL_SERVER_ERROR.value:
                return
        except Exception as e:
            print(f"Error waiting for service to be ready: {e}")  # noqa: T201
        time.sleep(0.5)
    msg = f"Service never became ready at {base_url}"
    raise RuntimeError(msg)


@pytest.fixture(scope="session")
def service_base_url(tmp_path_factory) -> None:  # noqa: ANN001
    """Start the real FastAPI service in a separate process (uvicorn) so we hit it over HTTP."""
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"

    env = os.environ.copy()

    # Ensure the child process can import your `src/` tree
    env["PYTHONPATH"] = os.pathsep.join([str(Path("src").resolve()), env.get("PYTHONPATH", "")])

    # Non-interactive Gmail (adjust if you have a token path env)
    env["MAIL_CLIENT_INTERACTIVE"] = "false"

    # Example if you need a token path:
    # env["GMAIL_TOKEN_FILE"] = os.path.abspath("token.json") # noqa: ERA001

    # === The key fix: target the module filename and point uvicorn at the directory ===
    cmd = [
        "uv",
        "run",
        "python",
        "-m",
        "uvicorn",
        "fast_api_service:app",  # module:var (src/mail_client_service/fast_api_service.py defines app = FastAPI(...))
        "--app-dir",
        "src/mail_client_service",  # directory that contains app.py
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
    ]

    proc = subprocess.Popen(  # noqa: S603
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=False,
    )

    try:
        _wait_for_ready(base_url, timeout_s=45)
    except Exception:
        if proc.stdout:
            pass
        proc.kill()
        raise

    yield base_url

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
