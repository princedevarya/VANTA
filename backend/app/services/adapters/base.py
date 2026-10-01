from dataclasses import dataclass


@dataclass
class ToolResult:
    tool: str
    command: str
    output: str
    return_code: int


class ToolAdapter:
    name = "base"

    async def run(self, target: str) -> ToolResult:
        raise NotImplementedError