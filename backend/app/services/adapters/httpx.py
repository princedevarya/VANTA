import asyncio

from app.services.adapters.base import ToolAdapter, ToolResult


class HttpxAdapter(ToolAdapter):
    name = "httpx"
    capabilities = (
        "http_probe",
        "technology_detection",
    )

    async def run(
        self,
        target: str,
        test_type: str = "technology_discovery",
    ) -> ToolResult:
        if test_type != "technology_discovery":
            raise ValueError(
                f"httpx does not support testing type: {test_type}"
            )

        command_args = [
            "httpx",
            "-u",
            target,
            "-silent",
            "-json",
            "-status-code",
            "-title",
            "-tech-detect",
            "-web-server",
        ]

        process = await asyncio.create_subprocess_exec(
            *command_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        output = stdout.decode(errors="replace")

        if stderr:
            output += "\n[stderr]\n"
            output += stderr.decode(errors="replace")

        return ToolResult(
            tool=self.name,
            command=" ".join(command_args),
            output=output,
            return_code=process.returncode,
            metadata={
                "target_type": "asset",
                "execution_mode": "testing",
                "test_type": test_type,
            },
        )