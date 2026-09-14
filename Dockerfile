# Syntax=docker/dockerfile:1.4
FROM python:3.10-slim

RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m appuser

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]