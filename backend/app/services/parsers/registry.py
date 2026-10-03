from collections.abc import Callable

from app.services.parsers.dns import parse_dns_output
from app.services.parsers.httpx import parse_httpx_output
from app.services.parsers.katana import parse_katana_output
from app.services.parsers.nmap import parse_nmap_output
from app.services.parsers.subfinder import parse_subfinder_output


Parser = Callable[[str], dict]


_PARSERS: dict[str, Parser] = {
    "dns": parse_dns_output,
    "httpx": parse_httpx_output,
    "katana": parse_katana_output,
    "nmap": parse_nmap_output,
    "subfinder": parse_subfinder_output,
}


def get_parser(tool: str) -> Parser | None:
    return _PARSERS.get(tool)