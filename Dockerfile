FROM python:3.13-slim-bookworm

WORKDIR /app

RUN echo 'Acquire::Retries "5";\nAcquire::ForceIPv4 "true";' > /etc/apt/apt.conf.d/99retries-ipv4

RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "main.py"]
