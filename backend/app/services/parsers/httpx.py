import json


def _technology_entry(value: str) -> dict[str, str]:
    value = value.strip()

    if not value:
        return {}

    if ":" in value:
        name, version = value.split(":", 1)
        name = name.strip()
        version = version.strip()

        if name and version:
            return {
                "name": name,
                "category": "technology",
                "version": version,
            }

    return {
        "name": value,
        "category": "technology",
        "version": "",
    }


def parse_httpx_output(output: str) -> dict:
    http_services: list[dict] = []
    technologies: list[dict[str, str]] = []

    for line in output.splitlines():
        line = line.strip()

        if not line or line.startswith("[stderr]"):
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue

        if not isinstance(record, dict):
            continue

        service = {
            "url": record.get("url"),
            "status_code": record.get("status_code"),
            "title": record.get("title"),
            "webserver": record.get("webserver"),
            "host": record.get("host"),
            "port": record.get("port"),
            "scheme": record.get("scheme"),
        }

        if any(value is not None for value in service.values()):
            http_services.append(service)

        webserver = record.get("webserver")

        if isinstance(webserver, str) and webserver.strip():
            entry = {
                "name": webserver.strip(),
                "category": "web_server",
                "version": "",
            }

            if entry not in technologies:
                technologies.append(entry)

        tech_values = record.get("tech")

        if isinstance(tech_values, str):
            tech_values = [tech_values]

        if isinstance(tech_values, list):
            for value in tech_values:
                if not isinstance(value, str):
                    continue

                entry = _technology_entry(value)

                if entry and entry not in technologies:
                    technologies.append(entry)

    return {
        "http_services": http_services,
        "technologies": technologies,
    }