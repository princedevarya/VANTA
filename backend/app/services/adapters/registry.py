from app.services.adapters.base import ToolAdapter
from app.services.adapters.dns import DnsAdapter
from app.services.adapters.httpx import HttpxAdapter
from app.services.adapters.katana import KatanaAdapter
from app.services.adapters.mock import MockAdapter
from app.services.adapters.nmap import NmapAdapter
from app.services.adapters.subfinder import SubfinderAdapter


_ADAPTERS: dict[str, ToolAdapter] = {
    "mock": MockAdapter(),
    "nmap": NmapAdapter(),
    "subfinder": SubfinderAdapter(),
    "httpx": HttpxAdapter(),
    "katana": KatanaAdapter(),
    "dns": DnsAdapter(),
}


def get_adapter(name: str) -> ToolAdapter:
    adapter = _ADAPTERS.get(name)

    if adapter is None:
        raise ValueError(f"Unknown tool adapter: {name}")

    return adapter