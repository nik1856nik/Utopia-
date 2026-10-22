FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
WORKDIR /app

COPY requirements.txt requirements.lock ./
RUN uv venv --python 3.12 "$VIRTUAL_ENV" \
    && uv pip sync --python "$VIRTUAL_ENV/bin/python" requirements.lock

COPY app ./app
EXPOSE 8001
CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
