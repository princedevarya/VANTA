import asyncio

from app.services.adapters.base import ToolAdapter, ToolResult


class NmapAdapter(ToolAdapter):
    name = "nmap"

    async def run(self, target: str) -> ToolResult:
        command_args = [
            "nmap",
            "-sV",
            target,
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
        )