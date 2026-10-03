import asyncio

from app.services.adapters.base import ToolAdapter, ToolResult


class DnsAdapter(ToolAdapter):
    name = "dns"

    capabilities = (
        "dns",
        "dns_enumeration",
    )

    async def run(
        self,
        target: str,
        test_type: str = "dns",
    ) -> ToolResult:
        if test_type != "dns":
            raise ValueError(
                f"dns adapter does not support testing type: {test_type}"
            )

        command_args = [
            "dig",
            target,
            "A",
            "+noall",
            "+answer",
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
                "execution_mode": "testing",
                "test_type": test_type,
                "record_type": "A",
            },
        )
