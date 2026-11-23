FROM python:3.11-slim AS build

COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src/ src/
RUN uv sync --frozen --no-dev --no-editable

FROM python:3.11-slim AS runtime

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATA_PROC_HOME=/app
WORKDIR /app
RUN groupadd --gid 10001 app && \
    useradd --uid 10001 --gid app --no-create-home app && \
    mkdir -p /app/data/processed && \
    chown 10001:10001 /app/data/processed
COPY --from=build /app/.venv /app/.venv
COPY examples/ examples/
COPY data/raw/ data/raw/
USER 10001:10001
ENTRYPOINT ["python"]
CMD ["examples/run_pipeline.py"]
