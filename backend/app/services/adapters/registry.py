from app.services.adapters.base import ToolAdapter
from app.services.adapters.mock import MockAdapter
from app.services.adapters.nmap import NmapAdapter


_ADAPTERS: dict[str, ToolAdapter] = {
    "mock": MockAdapter(),
    "nmap": NmapAdapter(),
}


def get_adapter(name: str) -> ToolAdapter:
    adapter = _ADAPTERS.get(name)

    if adapter is None:
        raise ValueError(f"Unknown tool adapter: {name}")

    return adapter