from dataclasses import dataclass, field


@dataclass
class ToolResult:
    tool: str
    command: str
    output: str
    return_code: int
    metadata: dict[str, str] = field(default_factory=dict)


class ToolAdapter:
    name = "base"

    capabilities: tuple[str, ...] = ()

    async def run(
        self,
        target: str,
        test_type: str | None = None,
    ) -> ToolResult:
        raise NotImplementedError