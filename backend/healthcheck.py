import sys
import urllib.request

HEALTH_URL = "http://127.0.0.1:8000/api/v1/health"


def main() -> int:
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=3) as response:
            if response.status != 200:
                return 1

            body = response.read().decode("utf-8", errors="replace")

            if '"status":"ok"' not in body:
                return 1

        return 0

    except Exception:
        return 1


if __name__ == "__main__":
    sys.exit(main())