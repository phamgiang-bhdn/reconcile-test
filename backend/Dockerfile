FROM python:3.12-slim

WORKDIR /app

# Goose (migration tool, binary Go) — single-file up/down SQL
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -fsSL https://github.com/pressly/goose/releases/latest/download/goose_linux_x86_64 \
         -o /usr/local/bin/goose \
    && chmod +x /usr/local/bin/goose \
    && apt-get purge -y curl && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ".[dev]"

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
