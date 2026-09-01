FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync --frozen
CMD ["sh", "-c", "uv run python -m worker.worker $(hostname)"]