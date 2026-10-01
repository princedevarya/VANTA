#!/usr/bin/env python3

import argparse
import json
import sys
import urllib.error
import urllib.request


DEFAULT_API = "http://localhost:8000/api/v1"


def request(method, path):
    url = f"{DEFAULT_API}{path}"

    req = urllib.request.Request(
        url,
        method=method,
        headers={
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req) as response:
            content_type = response.headers.get(
                "Content-Type",
                "",
            )

            data = response.read()

            if "application/json" in content_type:
                return json.loads(data.decode())

            return data.decode()

    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")

        try:
            error = json.loads(body)
            message = error.get("detail", body)
        except json.JSONDecodeError:
            message = body

        print(
            f"Error {exc.code}: {message}",
            file=sys.stderr,
        )
        sys.exit(1)

    except urllib.error.URLError as exc:
        print(
            f"Cannot connect to VANTA API: {exc.reason}",
            file=sys.stderr,
        )
        print(
            "Make sure FastAPI is running on "
            "http://localhost:8000",
            file=sys.stderr,
        )
        sys.exit(1)


def print_json(data):
    print(
        json.dumps(
            data,
            indent=2,
            default=str,
        )
    )


def cmd_health(_args):
    data = request(
        "GET",
        "/health",
    )

    print_json(data)


def cmd_services(args):
    data = request(
        "GET",
        f"/engagements/{args.engagement_id}/services",
    )

    if not data:
        print("No services found.")
        return

    print(
        f"{'PORT':<8}"
        f"{'PROTOCOL':<10}"
        f"{'STATE':<10}"
        f"SERVICE"
    )

    print("-" * 45)

    for service in data:
        print(
            f"{service['port']:<8}"
            f"{service['protocol']:<10}"
            f"{service['state']:<10}"
            f"{service['service']}"
        )


def cmd_dashboard(args):
    data = request(
        "GET",
        f"/engagements/{args.engagement_id}/dashboard",
    )

    print_json(data)


def cmd_coverage(args):
    data = request(
        "GET",
        f"/engagements/{args.engagement_id}/testing-coverage",
    )

    print_json(data)


def cmd_findings(args):
    data = request(
        "GET",
        f"/engagements/{args.engagement_id}/findings",
    )

    if not data:
        print("No findings found.")
        return

    print(
        f"{'ID':<38}"
        f"{'SEVERITY':<12}"
        f"{'STATUS':<10}"
        f"TITLE"
    )

    print("-" * 100)

    for finding in data:
        print(
            f"{finding['id']:<38}"
            f"{finding['severity']:<12}"
            f"{finding['status']:<10}"
            f"{finding['title']}"
        )


def cmd_report(args):
    url = (
        f"{DEFAULT_API}"
        f"/engagements/{args.engagement_id}/report"
    )

    req = urllib.request.Request(
        url,
        method="GET",
    )

    try:
        with urllib.request.urlopen(req) as response:
            content_disposition = response.headers.get(
                "Content-Disposition",
                "",
            )

            filename = "vanta_report.md"

            if "filename=" in content_disposition:
                filename = (
                    content_disposition
                    .split("filename=", 1)[1]
                    .strip()
                    .strip('"')
                )

            output_path = args.output or filename

            with open(
                output_path,
                "wb",
            ) as output_file:
                output_file.write(
                    response.read()
                )

            print(
                f"Report generated: {output_path}"
            )

    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        print(
            f"Error {exc.code}: {body}",
            file=sys.stderr,
        )
        sys.exit(1)

    except urllib.error.URLError as exc:
        print(
            f"Cannot connect to VANTA API: {exc.reason}",
            file=sys.stderr,
        )
        sys.exit(1)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="vanta",
        description=(
            "VANTA - Virtual Attack & "
            "Network Testing Arena"
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # ---------------------------------------------------------
    # health
    # ---------------------------------------------------------
    health_parser = subparsers.add_parser(
        "health",
        help="Check VANTA API health",
    )

    health_parser.set_defaults(
        func=cmd_health,
    )

    # ---------------------------------------------------------
    # services
    # ---------------------------------------------------------
    services_parser = subparsers.add_parser(
        "services",
        help="List discovered services",
    )

    services_parser.add_argument(
        "engagement_id",
        help="Engagement UUID",
    )

    services_parser.set_defaults(
        func=cmd_services,
    )

    # ---------------------------------------------------------
    # dashboard
    # ---------------------------------------------------------
    dashboard_parser = subparsers.add_parser(
        "dashboard",
        help="Show engagement dashboard",
    )

    dashboard_parser.add_argument(
        "engagement_id",
        help="Engagement UUID",
    )

    dashboard_parser.set_defaults(
        func=cmd_dashboard,
    )

    # ---------------------------------------------------------
    # coverage
    # ---------------------------------------------------------
    coverage_parser = subparsers.add_parser(
        "coverage",
        help="Show testing coverage",
    )

    coverage_parser.add_argument(
        "engagement_id",
        help="Engagement UUID",
    )

    coverage_parser.set_defaults(
        func=cmd_coverage,
    )

    # ---------------------------------------------------------
    # findings
    # ---------------------------------------------------------
    findings_parser = subparsers.add_parser(
        "findings",
        help="List findings",
    )

    findings_parser.add_argument(
        "engagement_id",
        help="Engagement UUID",
    )

    findings_parser.set_defaults(
        func=cmd_findings,
    )

    # ---------------------------------------------------------
    # report
    # ---------------------------------------------------------
    report_parser = subparsers.add_parser(
        "report",
        help="Generate pentest report",
    )

    report_parser.add_argument(
        "engagement_id",
        help="Engagement UUID",
    )

    report_parser.add_argument(
        "-o",
        "--output",
        help="Output report path",
    )

    report_parser.set_defaults(
        func=cmd_report,
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()