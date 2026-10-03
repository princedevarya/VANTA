import asyncio

from app.services.adapters.base import ToolAdapter, ToolResult


class SubfinderAdapter(ToolAdapter):
    name = "subfinder"

    capabilities = (
        "subdomain_discovery",
    )

    async def run(
        self,
        target: str,
        test_type: str = "subdomain_discovery",
    ) -> ToolResult:
        if test_type != "subdomain_discovery":
            raise ValueError(
                f"subfinder does not support testing type: {test_type}"
            )

        command_args = [
            "subfinder",
            "-d",
            target,
            "-silent",
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
                "target_type": "domain",
                "execution_mode": "local",
            },
        )