import json
from urllib.parse import urlsplit


MAX_ENDPOINTS = 2000


def parse_katana_output(output: str) -> dict:
    endpoints: list[dict] = []
    seen: set[tuple[str, str]] = set()

    parsed_records = 0
    invalid_records = 0
    duplicate_records = 0
    endpoint_limit_reached = False

    for line in output.splitlines():
        line = line.strip()

        if not line or line.startswith("[stderr]"):
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            invalid_records += 1
            continue

        parsed_records += 1

        if not isinstance(record, dict):
            invalid_records += 1
            continue

        request = record.get("request")

        if not isinstance(request, dict):
            invalid_records += 1
            continue

        url = request.get("endpoint")

        if not isinstance(url, str) or not url.strip():
            invalid_records += 1
            continue

        url = url.strip()

        method = request.get("method", "GET")

        if not isinstance(method, str):
            method = "GET"

        method = method.upper()

        dedupe_key = (method, url)

        if dedupe_key in seen:
            duplicate_records += 1
            continue

        if len(endpoints) >= MAX_ENDPOINTS:
            endpoint_limit_reached = True
            break

        seen.add(dedupe_key)

        parsed_url = urlsplit(url)

        response = record.get("response")

        if not isinstance(response, dict):
            response = {}

        status_code = response.get("status_code")

        try:
            status_code = (
                int(status_code)
                if status_code is not None
                else None
            )
        except (TypeError, ValueError):
            status_code = None

        headers = response.get("headers")

        if not isinstance(headers, dict):
            headers = {}

        endpoint = {
            "url": url,
            "method": method,
            "scheme": parsed_url.scheme or None,
            "host": parsed_url.hostname,
            "port": parsed_url.port,
            "path": parsed_url.path or "/",
            "query": parsed_url.query or None,
            "status_code": status_code,
            "content_type": headers.get("Content-Type"),
            "server": headers.get("Server"),
            "source_url": request.get("source"),
            "tag": request.get("tag"),
            "attribute": request.get("attribute"),
            "timestamp": record.get("timestamp"),
        }

        endpoints.append(endpoint)

    return {
        "endpoints": endpoints,
        "endpoint_count": len(endpoints),
        "parsed_records": parsed_records,
        "invalid_records": invalid_records,
        "duplicate_records": duplicate_records,
        "endpoint_limit": MAX_ENDPOINTS,
        "endpoint_limit_reached": endpoint_limit_reached,
    }
