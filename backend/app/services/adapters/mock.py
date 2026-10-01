from app.services.adapters.base import ToolAdapter, ToolResult


class MockAdapter(ToolAdapter):
    name = "mock"

    async def run(self, target: str) -> ToolResult:
        command = f"mock-scan {target}"

        output = (
            f"Mock scan completed for {target}\n"
            "PORT 80/tcp open http\n"
            "PORT 443/tcp open https\n"
        )

        return ToolResult(
            tool=self.name,
            command=command,
            output=output,
            return_code=0,
        )