FROM python:3.11-slim

# Install curl for uv installer
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

ENV UV_PROJECT_ENVIRONMENT=.venv

WORKDIR /app

COPY pyproject.toml uv.lock ./


COPY src ./src

RUN uv sync --no-dev

EXPOSE 8000

WORKDIR /app/src/mail_client_service

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
