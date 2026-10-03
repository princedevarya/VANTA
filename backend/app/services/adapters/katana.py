import asyncio

from app.services.adapters.base import ToolAdapter, ToolResult


MAX_OUTPUT_BYTES = 4 * 1024 * 1024
MAX_LINE_BYTES = 8 * 1024 * 1024
KATANA_DEPTH = "1"


class KatanaAdapter(ToolAdapter):
    name = "katana"
    capabilities = (
        "endpoint_discovery",
        "web_crawling",
    )

    async def run(
        self,
        target: str,
        test_type: str = "endpoint_discovery",
    ) -> ToolResult:
        if test_type != "endpoint_discovery":
            raise ValueError(
                f"katana adapter does not support testing type: {test_type}"
            )

        command_args = [
            "katana",
            "-u",
            target,
            "-silent",
            "-j",
            "-d",
            KATANA_DEPTH,
        ]

        process = await asyncio.create_subprocess_exec(
            *command_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            limit=MAX_LINE_BYTES,
        )

        stdout_chunks: list[bytes] = []
        stdout_size = 0
        output_truncated = False

        try:
            while True:
                try:
                    line = await process.stdout.readline()
                except asyncio.LimitOverrunError:
                    output_truncated = True

                    # Drain the oversized line so the subprocess
                    # can continue and eventually terminate cleanly.
                    while True:
                        try:
                            chunk = await process.stdout.read(64 * 1024)
                        except Exception:
                            chunk = b""

                        if not chunk:
                            break

                        if b"\n" in chunk:
                            break

                    continue

                if not line:
                    break

                if stdout_size < MAX_OUTPUT_BYTES:
                    remaining = MAX_OUTPUT_BYTES - stdout_size

                    if len(line) <= remaining:
                        stdout_chunks.append(line)
                        stdout_size += len(line)
                    else:
                        stdout_chunks.append(line[:remaining])
                        stdout_size += remaining
                        output_truncated = True
                else:
                    output_truncated = True

        finally:
            stderr = await process.stderr.read()
            return_code = await process.wait()

        output = b"".join(stdout_chunks).decode(
            errors="replace"
        )

        if stderr:
            stderr_text = stderr.decode(errors="replace")

            if output:
                output += "\n"

            output += "[stderr]\n"
            output += stderr_text

        metadata = {
            "target_type": "asset",
            "execution_mode": "testing",
            "test_type": test_type,
            "depth": KATANA_DEPTH,
            "output_format": "jsonl",
            "output_limit_bytes": str(MAX_OUTPUT_BYTES),
            "stream_line_limit_bytes": str(MAX_LINE_BYTES),
            "output_truncated": str(output_truncated).lower(),
        }

        return ToolResult(
            tool=self.name,
            command=" ".join(command_args),
            output=output,
            return_code=return_code,
            metadata=metadata,
        )