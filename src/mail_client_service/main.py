import os
import sys


def _ensure_import_paths() -> None:
    """Ensure local src paths are importable when running from source.

    This lets `python src/mail_client_service/main.py` import the package
    without requiring an installation step.
    """
    current_dir = os.path.dirname(__file__)

    # Add this package's internal src/ to sys.path
    package_src = os.path.join(current_dir, "src")
    if os.path.isdir(package_src) and package_src not in sys.path:
        sys.path.insert(0, package_src)

    # Add the workspace-level src/ so sibling packages are importable
    repo_root = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
    workspace_src = os.path.join(repo_root, "src")
    if os.path.isdir(workspace_src) and workspace_src not in sys.path:
        sys.path.insert(0, workspace_src)


def main() -> None:
    _ensure_import_paths()

    import uvicorn  # noqa: WPS433 (import inside function for CLI speed)
    from mail_client_service.main import app  # noqa: WPS433

    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    reload = os.environ.get("RELOAD", "false").lower() in {"1", "true", "yes"}

    uvicorn.run(app, host=host, port=port, reload=reload)

if __name__ == "__main__":
    main()
