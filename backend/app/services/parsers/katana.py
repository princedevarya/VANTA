import json
from urllib.parse import urlsplit


def _parse_status_code(value):
    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_string(value):
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()
        return value or None

    return str(value)


def parse_katana_output(output: str) -> dict:
    """
    Parse Katana JSONL output.

    The adapter controls the maximum amount of raw output that
    reaches this parser. This function therefore focuses on
    extracting normalized endpoint inventory records.

    Duplicate endpoints are removed using:
        METHOD + URL
    """

    endpoints: list[dict] = []

    seen: set[tuple[str, str]] = set()

    parsed_records = 0
    invalid_records = 0
    duplicate_records = 0

    for line in output.splitlines():
        line = line.strip()

        if not line:
            continue

        # Adapter may append stderr after stdout.
        if line.startswith("[stderr]"):
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

        if not isinstance(url, str):
            invalid_records += 1
            continue

        url = url.strip()

        if not url:
            invalid_records += 1
            continue

        method = request.get(
            "method",
            "GET",
        )

        if not isinstance(method, str):
            method = "GET"

        method = method.upper().strip()

        if not method:
            method = "GET"

        dedupe_key = (
            method,
            url,
        )

        if dedupe_key in seen:
            duplicate_records += 1
            continue

        seen.add(dedupe_key)

        try:
            parsed_url = urlsplit(url)
            port = parsed_url.port
        except ValueError:
            invalid_records += 1
            continue

        response = record.get("response")

        if not isinstance(response, dict):
            response = {}

        status_code = _parse_status_code(
            response.get("status_code")
        )

        headers = response.get("headers")

        if not isinstance(headers, dict):
            headers = {}

        endpoint = {
            "url": url,
            "method": method,

            "scheme": (
                parsed_url.scheme
                or None
            ),

            "host": (
                parsed_url.hostname
                or None
            ),

            "port": port,

            "path": (
                parsed_url.path
                or "/"
            ),

            "query": (
                parsed_url.query
                or None
            ),

            "status_code": status_code,

            "content_type": _safe_string(
                headers.get("Content-Type")
            ),

            "server": _safe_string(
                headers.get("Server")
            ),

            "source_url": _safe_string(
                request.get("source")
            ),

            "tag": _safe_string(
                request.get("tag")
            ),

            "attribute": _safe_string(
                request.get("attribute")
            ),

            "timestamp": _safe_string(
                record.get("timestamp")
            ),
        }

        endpoints.append(endpoint)

    return {
        "endpoints": endpoints,
        "endpoint_count": len(endpoints),
        "parsed_records": parsed_records,
        "invalid_records": invalid_records,
        "duplicate_records": duplicate_records,
    }
