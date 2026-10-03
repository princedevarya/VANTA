def parse_subfinder_output(output: str) -> dict:
    subdomains: list[str] = []

    for line in output.splitlines():
        value = line.strip().lower().rstrip(".")

        if not value:
            continue

        if value.startswith("[stderr]"):
            continue

        if value not in subdomains:
            subdomains.append(value)

    return {
        "subdomains": subdomains,
    }