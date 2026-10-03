def parse_dns_output(output: str) -> dict:
    records = []

    for line in output.splitlines():
        line = line.strip()

        if not line or line.startswith(";"):
            continue

        parts = line.split()

        if len(parts) < 5:
            continue

        records.append(
            {
                "name": parts[0],
                "ttl": parts[1],
                "class": parts[2],
                "type": parts[3],
                "value": " ".join(parts[4:]),
            }
        )

    return {
        "records": records,
        "record_count": len(records),
    }
