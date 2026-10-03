import asyncio

from app.services.adapters.base import ToolAdapter, ToolResult


class NmapAdapter(ToolAdapter):
    name = "nmap"
    capabilities = (
        "port_enumeration",
        "service_enumeration",
    )

    async def run(
        self,
        target: str,
        test_type: str = "service_enumeration",
    ) -> ToolResult:
        # Keep the interactive VANTA workflow responsive. A full 65,535-port
        # scan (-p-) can exceed the reverse-proxy/request timeout on internet
        # targets. Deep/full-port scanning can be added as a separate mode.
        if test_type == "port_enumeration":
            command_args = [
                "nmap",
                "-T4",
                "--top-ports",
                "1000",
                "--open",
                target,
            ]
        elif test_type == "service_enumeration":
            command_args = [
                "nmap",
                "-sV",
                "-T4",
                "--top-ports",
                "1000",
                "--open",
                target,
            ]
        else:
            raise ValueError(
                f"nmap does not support testing type: {test_type}"
            )

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
                "scan_profile": "top_1000_open",
            },
        )
