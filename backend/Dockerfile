# ---------------------------------------------------------
# VANTA - Tool Build Stage
# ---------------------------------------------------------
FROM golang:1.26-bookworm AS tools

RUN GOBIN=/usr/local/bin \
    go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@v2.16.0

RUN GOBIN=/usr/local/bin \
    go install github.com/projectdiscovery/httpx/cmd/httpx@v1.12.0

RUN CGO_ENABLED=1 GOBIN=/usr/local/bin \
    go install github.com/projectdiscovery/katana/cmd/katana@v1.7.0


# ---------------------------------------------------------
# VANTA - Backend Runtime
# ---------------------------------------------------------
FROM python:3.14-slim-bookworm

WORKDIR /app

# Security/recon tools required by VANTA adapters.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        nmap \
        dnsutils \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built Go security tooling.
COPY --from=tools /usr/local/bin/subfinder /usr/local/bin/subfinder
COPY --from=tools /usr/local/bin/httpx /usr/local/bin/httpx
COPY --from=tools /usr/local/bin/katana /usr/local/bin/katana

# Python dependencies.
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# VANTA application.
COPY app ./app
COPY healthcheck.py ./healthcheck.py

# Runtime directories.
RUN mkdir -p /app/reports

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]