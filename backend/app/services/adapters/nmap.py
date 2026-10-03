import asyncio

from app.services.adapters.base import ToolAdapter, ToolResult


class NmapAdapter(ToolAdapter):
    name = "nmap"

    capabilities = (
        "port_enumeration",
        "service_enumeration",
        "network_configuration",
    )

    async def run(
        self,
        target: str,
        test_type: str = "service_enumeration",
    ) -> ToolResult:

        if test_type == "port_enumeration":
            command_args = [
                "nmap",
                "-T4",
                "--top-ports",
                "1000",
                "--open",
                target,
            ]

            scan_profile = "top_1000_open"

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

            scan_profile = "service_detection_top_1000"

        elif test_type == "network_configuration":
            command_args = [
                "nmap",
                "-sV",
                "-T4",
                "--top-ports",
                "1000",
                "--open",
                "--reason",
                target,
            ]

            scan_profile = "network_configuration_observation"

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

        output = stdout.decode(
            errors="replace"
        )

        if stderr:
            output += "\n[stderr]\n"
            output += stderr.decode(
                errors="replace"
            )

        return ToolResult(
            tool=self.name,
            command=" ".join(command_args),
            output=output,
            return_code=process.returncode,
            metadata={
                "target_type": "asset",
                "execution_mode": "testing",
                "test_type": test_type,
                "scan_profile": scan_profile,
            },
        )
