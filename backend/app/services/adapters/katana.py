import asyncio

from app.services.adapters.base import ToolAdapter, ToolResult


# Katana can produce very large JSONL records.
# Keep the process bounded so a single target cannot exhaust
# the VANTA backend container.
MAX_OUTPUT_BYTES = 4 * 1024 * 1024
MAX_LINE_BYTES = 8 * 1024 * 1024

# Depth 1 is intentional for the first endpoint-discovery pass.
# Deeper crawling should be an explicit future operator option.
KATANA_DEPTH = "1"

READ_CHUNK_BYTES = 64 * 1024


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
        oversized_lines = 0
        output_lines = 0

        try:
            while True:
                try:
                    line = await process.stdout.readline()

                except asyncio.LimitOverrunError:
                    # A single JSON record exceeded MAX_LINE_BYTES.
                    # Drain until the newline so the subprocess can
                    # continue without poisoning the StreamReader.
                    oversized_lines += 1
                    output_truncated = True

                    while True:
                        chunk = await process.stdout.read(
                            READ_CHUNK_BYTES
                        )

                        if not chunk:
                            break

                        if b"\n" in chunk:
                            break

                    continue

                if not line:
                    break

                output_lines += 1

                if stdout_size >= MAX_OUTPUT_BYTES:
                    output_truncated = True
                    continue

                remaining = MAX_OUTPUT_BYTES - stdout_size

                if len(line) <= remaining:
                    stdout_chunks.append(line)
                    stdout_size += len(line)

                else:
                    stdout_chunks.append(line[:remaining])
                    stdout_size += remaining
                    output_truncated = True

        finally:
            stderr = await process.stderr.read()
            return_code = await process.wait()

        output = b"".join(stdout_chunks).decode(
            errors="replace"
        )

        if stderr:
            stderr_text = stderr.decode(
                errors="replace"
            ).strip()

            if stderr_text:
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
            "output_truncated": str(
                output_truncated
            ).lower(),
            "oversized_lines": str(
                oversized_lines
            ),
            "output_lines": str(
                output_lines
            ),
            "captured_output_bytes": str(
                stdout_size
            ),
        }

        return ToolResult(
            tool=self.name,
            command=" ".join(command_args),
            output=output,
            return_code=return_code,
            metadata=metadata,
        )