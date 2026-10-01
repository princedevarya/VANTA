import re


PORT_PATTERN = re.compile(
    r"^(?:PORT\s+)?"
    r"(?P<port>\d+)/(?P<protocol>\S+)\s+"
    r"(?P<state>\S+)\s+"
    r"(?P<service>\S+)"
)


def parse_nmap_output(output: str) -> dict:
    host = None
    services = []

    for line in output.splitlines():
        line = line.strip()

        # Standard Nmap:
        # Nmap scan report for example.com (172.66.147.243)
        if line.startswith("Nmap scan report for "):
            host = line.replace(
                "Nmap scan report for ",
                "",
                1,
            )

            if " (" in host:
                host = host.split(" (", 1)[0]

        # Supports both:
        #
        # Standard Nmap:
        # 80/tcp   open  http
        #
        # VANTA Mock adapter:
        # PORT 80/tcp open http
        match = PORT_PATTERN.match(line)

        if match:
            services.append(
                {
                    "port": int(match.group("port")),
                    "protocol": match.group("protocol"),
                    "state": match.group("state"),
                    "service": match.group("service"),
                }
            )

    return {
        "host": host,
        "services": services,
    }