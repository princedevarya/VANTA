from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Activity,
    Asset,
    Engagement,
    Evidence,
    Finding,
    Scope,
    Service,
)
from app.services.coverage import get_testing_coverage


REPORTS_DIR = Path(__file__).resolve().parents[3] / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def safe_filename(value: str) -> str:
    return "".join(
        character if character.isalnum() or character in "-_" else "_"
        for character in value
    )


def markdown_cell(value: object) -> str:
    """Keep generated Markdown tables valid when values contain pipes/newlines."""
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def display_id(value: str | None) -> str:
    """Show a compact identifier while keeping full IDs in traceability blocks."""
    if not value:
        return "N/A"
    return value[:8]


def status_label(value: str | None) -> str:
    if not value:
        return "N/A"
    return value.replace("_", " ").title()


async def generate_report(
    db: AsyncSession,
    *,
    engagement_id: str,
) -> tuple[str, str]:

    # ---------------------------------------------------------
    # Engagement
    # ---------------------------------------------------------
    result = await db.execute(
        select(Engagement).where(
            Engagement.id == engagement_id
        )
    )
    engagement = result.scalar_one_or_none()

    if engagement is None:
        raise ValueError("Engagement not found")

    # ---------------------------------------------------------
    # Assets
    # ---------------------------------------------------------
    result = await db.execute(
        select(Asset)
        .where(
            Asset.engagement_id == engagement_id
        )
        .order_by(Asset.created_at)
    )
    assets = result.scalars().all()

    # ---------------------------------------------------------
    # Scope
    # ---------------------------------------------------------
    result = await db.execute(
        select(Scope)
        .where(
            Scope.engagement_id == engagement_id
        )
        .order_by(Scope.created_at)
    )
    scopes = result.scalars().all()

    # ---------------------------------------------------------
    # Services
    # ---------------------------------------------------------
    result = await db.execute(
        select(Service)
        .where(
            Service.engagement_id == engagement_id
        )
        .order_by(
            Service.asset_id,
            Service.port,
        )
    )
    services = result.scalars().all()

    # ---------------------------------------------------------
    # Activities
    # ---------------------------------------------------------
    result = await db.execute(
        select(Activity)
        .where(
            Activity.engagement_id == engagement_id
        )
        .order_by(Activity.created_at)
    )
    activities = result.scalars().all()

    # ---------------------------------------------------------
    # Evidence
    # ---------------------------------------------------------
    result = await db.execute(
        select(Evidence)
        .where(
            Evidence.engagement_id == engagement_id
        )
        .order_by(Evidence.created_at)
    )
    evidence = result.scalars().all()

    # ---------------------------------------------------------
    # Findings
    # ---------------------------------------------------------
    result = await db.execute(
        select(Finding)
        .where(
            Finding.engagement_id == engagement_id
        )
        .order_by(Finding.created_at)
    )
    findings = result.scalars().all()

    # ---------------------------------------------------------
    # Testing coverage
    # ---------------------------------------------------------
    coverage = await get_testing_coverage(
        db,
        engagement_id=engagement_id,
    )

    # ---------------------------------------------------------
    # Lookup maps used to make the report human-readable.
    # ---------------------------------------------------------
    asset_by_id = {
        asset.id: asset
        for asset in assets
    }

    activity_by_id = {
        activity.id: activity
        for activity in activities
    }

    evidence_by_id = {
        item.id: item
        for item in evidence
    }

    # An evidence item normally belongs to at most one finding, but
    # keep a list so the report remains correct if that changes later.
    findings_by_evidence_id: dict[str, list[str]] = {}

    for index, finding in enumerate(findings, start=1):
        finding_ref = f"VANTA-{index:03d}"

        for evidence_id in (
            finding.evidence_id,
            finding.retest_evidence_id,
        ):
            if evidence_id:
                findings_by_evidence_id.setdefault(
                    evidence_id,
                    [],
                ).append(finding_ref)

    # ---------------------------------------------------------
    # Build report
    # ---------------------------------------------------------
    report: list[str] = []

    report.append("# VANTA Penetration Testing Report")
    report.append("")
    report.append(
        f"**Generated:** {datetime.utcnow().isoformat()} UTC"
    )
    report.append("")
    report.append("---")
    report.append("")

    # ---------------------------------------------------------
    # Engagement
    # ---------------------------------------------------------
    report.append("## 1. Engagement Information")
    report.append("")
    report.append("| Field | Value |")
    report.append("|---|---|")
    report.append(
        f"| Engagement | {markdown_cell(engagement.name)} |"
    )
    report.append(
        f"| Client | {markdown_cell(engagement.client or 'N/A')} |"
    )
    report.append(
        f"| Status | {status_label(engagement.status)} |"
    )
    report.append(
        f"| Description | "
        f"{markdown_cell(engagement.description or 'N/A')} |"
    )
    report.append("")

    # ---------------------------------------------------------
    # Scope
    # ---------------------------------------------------------
    report.append("## 2. Scope")
    report.append("")

    if scopes:
        report.append(
            "| Target | Type | Scope | Description |"
        )
        report.append("|---|---|---|---|")

        for scope in scopes:
            report.append(
                f"| `{markdown_cell(scope.target)}` | "
                f"{markdown_cell(scope.target_type)} | "
                f"{status_label(scope.scope_type)} | "
                f"{markdown_cell(scope.description or '')} |"
            )
        report.append("")
    else:
        report.append("No scope entries recorded.")
        report.append("")

    # ---------------------------------------------------------
    # Executive Summary
    # ---------------------------------------------------------
    validated_findings = [
        finding
        for finding in findings
        if finding.validation_status == "validated"
    ]

    open_findings = [
        finding
        for finding in findings
        if finding.status == "open"
    ]

    closed_findings = [
        finding
        for finding in findings
        if finding.status == "closed"
    ]

    report.append("## 3. Executive Summary")
    report.append("")
    report.append("| Metric | Count |")
    report.append("|---|---:|")
    report.append(f"| Assets | {len(assets)} |")
    report.append(f"| Services | {len(services)} |")
    report.append(f"| Activities | {len(activities)} |")
    report.append(f"| Evidence Items | {len(evidence)} |")
    report.append(f"| Findings | {len(findings)} |")
    report.append(
        f"| Validated Findings | {len(validated_findings)} |"
    )
    report.append(f"| Open Findings | {len(open_findings)} |")
    report.append(f"| Closed Findings | {len(closed_findings)} |")
    report.append("")

    # ---------------------------------------------------------
    # Attack Surface
    # ---------------------------------------------------------
    report.append("## 4. Attack Surface")
    report.append("")
    report.append("### Assets")
    report.append("")

    report.append("| Asset | Type | Status |")
    report.append("|---|---|---|")

    if assets:
        for asset in assets:
            report.append(
                f"| `{markdown_cell(asset.value)}` | "
                f"{markdown_cell(asset.asset_type)} | "
                f"{status_label(asset.status)} |"
            )
    else:
        report.append("| — | — | No assets recorded |")

    report.append("")
    report.append("### Services")
    report.append("")

    if services:
        report.append(
            "| Asset | Port | Protocol | State | Service |"
        )
        report.append("|---|---:|---|---|---|")

        for service in services:
            asset = asset_by_id.get(service.asset_id)
            asset_name = (
                asset.value
                if asset
                else display_id(service.asset_id)
            )

            report.append(
                f"| `{markdown_cell(asset_name)}` | "
                f"{service.port} | "
                f"{markdown_cell(service.protocol)} | "
                f"{status_label(service.state)} | "
                f"{markdown_cell(service.service)} |"
            )
    else:
        report.append("No services recorded.")

    report.append("")

    # ---------------------------------------------------------
    # Testing Coverage
    # ---------------------------------------------------------
    report.append("## 5. Testing Coverage")
    report.append("")

    for area, tests in coverage.items():
        tested_count = sum(
            1 for status in tests.values()
            if status == "tested"
        )
        total_count = len(tests)

        report.append(
            f"### {'API' if area == 'api' else area.title()} "
            f"({tested_count}/{total_count} tested)"
        )
        report.append("")
        report.append("| Test | Status |")
        report.append("|---|---|")

        for test_type, status in tests.items():
            report.append(
                f"| `{markdown_cell(test_type)}` | "
                f"{status_label(status)} |"
            )

        report.append("")

    # ---------------------------------------------------------
    # Findings
    # ---------------------------------------------------------
    report.append("## 6. Findings")
    report.append("")

    if not findings:
        report.append("No findings recorded.")
        report.append("")
    else:
        for index, finding in enumerate(findings, start=1):
            finding_ref = f"VANTA-{index:03d}"

            asset = asset_by_id.get(finding.asset_id)
            activity = activity_by_id.get(finding.activity_id)
            original_evidence = evidence_by_id.get(
                finding.evidence_id
            )
            retest_activity = activity_by_id.get(
                finding.retest_activity_id
            )
            retest_evidence = evidence_by_id.get(
                finding.retest_evidence_id
            )

            report.append(
                f"### {finding_ref} — "
                f"{markdown_cell(finding.title)}"
            )
            report.append("")
            report.append("| Field | Value |")
            report.append("|---|---|")
            report.append(
                f"| Severity | {status_label(finding.severity)} |"
            )
            report.append(
                f"| Status | {status_label(finding.status)} |"
            )
            report.append(
                f"| Validation | "
                f"{status_label(finding.validation_status)} |"
            )
            report.append(
                f"| Affected Asset | "
                f"{markdown_cell(asset.value if asset else 'N/A')} |"
            )
            report.append("")

            report.append("#### Description")
            report.append("")
            report.append(
                finding.description
                or "No description provided."
            )
            report.append("")

            report.append("#### Remediation")
            report.append("")
            report.append(
                finding.remediation
                or "No remediation provided."
            )
            report.append("")

            report.append("#### Retesting")
            report.append("")
            report.append("| Field | Value |")
            report.append("|---|---|")
            report.append(
                f"| Retest Status | "
                f"{status_label(finding.retest_status or 'not_retested')} |"
            )
            report.append(
                f"| Retest Activity | "
                f"{markdown_cell(retest_activity.title if retest_activity else 'N/A')} |"
            )
            report.append(
                f"| Retest Evidence | "
                f"{markdown_cell(retest_evidence.title if retest_evidence else 'N/A')} |"
            )
            report.append("")

            report.append("#### Traceability")
            report.append("")
            report.append("| Relationship | Reference |")
            report.append("|---|---|")

            if activity:
                report.append(
                    f"| Testing Activity | "
                    f"`{display_id(activity.id)}` — "
                    f"{markdown_cell(activity.title)} |"
                )
            else:
                report.append("| Testing Activity | N/A |")

            if original_evidence:
                report.append(
                    f"| Evidence | "
                    f"`{display_id(original_evidence.id)}` — "
                    f"{markdown_cell(original_evidence.title)} |"
                )
            else:
                report.append("| Evidence | N/A |")

            if retest_activity:
                report.append(
                    f"| Retest Activity | "
                    f"`{display_id(retest_activity.id)}` — "
                    f"{markdown_cell(retest_activity.title)} |"
                )
            else:
                report.append("| Retest Activity | N/A |")

            if retest_evidence:
                report.append(
                    f"| Retest Evidence | "
                    f"`{display_id(retest_evidence.id)}` — "
                    f"{markdown_cell(retest_evidence.title)} |"
                )
            else:
                report.append("| Retest Evidence | N/A |")

            report.append("")
            report.append(
                "<details>"
            )
            report.append("<summary>Internal identifiers</summary>")
            report.append("")
            report.append(
                f"- Finding ID: `{finding.id}`"
            )
            report.append(
                f"- Asset ID: `{finding.asset_id or 'N/A'}`"
            )
            report.append(
                f"- Activity ID: `{finding.activity_id or 'N/A'}`"
            )
            report.append(
                f"- Evidence ID: `{finding.evidence_id or 'N/A'}`"
            )
            report.append(
                f"- Retest Activity ID: "
                f"`{finding.retest_activity_id or 'N/A'}`"
            )
            report.append(
                f"- Retest Evidence ID: "
                f"`{finding.retest_evidence_id or 'N/A'}`"
            )
            report.append("")
            report.append("</details>")
            report.append("")

    # ---------------------------------------------------------
    # Evidence
    # ---------------------------------------------------------
    report.append("## 7. Evidence")
    report.append("")

    if not evidence:
        report.append("No evidence recorded.")
        report.append("")
    else:
        finding_evidence_ids = {
            finding.evidence_id
            for finding in findings
            if finding.evidence_id
        }
        retest_evidence_ids = {
            finding.retest_evidence_id
            for finding in findings
            if finding.retest_evidence_id
        }

        finding_evidence = [
            item
            for item in evidence
            if item.id in finding_evidence_ids
        ]
        retest_evidence = [
            item
            for item in evidence
            if item.id in retest_evidence_ids
        ]
        general_evidence = [
            item
            for item in evidence
            if item.id not in finding_evidence_ids
            and item.id not in retest_evidence_ids
        ]

        def append_evidence_item(
            item: Evidence,
            *,
            related_findings: list[str] | None = None,
        ) -> None:
            asset = asset_by_id.get(item.asset_id)
            activity = activity_by_id.get(item.activity_id)
            related_findings = related_findings or findings_by_evidence_id.get(
                item.id,
                [],
            )

            report.append(
                f"#### {markdown_cell(item.title)}"
            )
            report.append("")
            report.append("| Field | Value |")
            report.append("|---|---|")
            report.append(
                f"| Type | {markdown_cell(item.evidence_type)} |"
            )
            report.append(
                f"| Asset | "
                f"{markdown_cell(asset.value if asset else 'N/A')} |"
            )
            report.append(
                f"| Activity | "
                f"{markdown_cell(activity.title if activity else 'N/A')} |"
            )

            if related_findings:
                report.append(
                    f"| Related Finding(s) | "
                    f"{', '.join(related_findings)} |"
                )

            report.append("")
            report.append("<details>")
            report.append("<summary>Evidence content</summary>")
            report.append("")

            if item.content:
                report.append("```text")
                report.append(item.content.rstrip())
                report.append("```")
            elif item.file_path:
                report.append(
                    f"Evidence file: `{item.file_path}`"
                )
            else:
                report.append("No evidence content recorded.")

            report.append("")
            report.append("</details>")
            report.append("")
            report.append(
                f"Internal evidence ID: `{item.id}`"
            )
            report.append("")

        if finding_evidence:
            report.append("### 7.1 Finding Evidence")
            report.append("")
            report.append(
                "Evidence directly linked to one or more findings."
            )
            report.append("")
            for item in finding_evidence:
                append_evidence_item(item)

        if retest_evidence:
            report.append("### 7.2 Retest Evidence")
            report.append("")
            report.append(
                "Evidence collected while validating remediation "
                "during retesting."
            )
            report.append("")
            for item in retest_evidence:
                append_evidence_item(item)

        if general_evidence:
            report.append("### 7.3 Assessment Evidence")
            report.append("")
            report.append(
                f"{len(general_evidence)} evidence item(s) "
                "recorded during the assessment but not directly "
                "linked to a finding."
            )
            report.append("")

            report.append("<details>")
            report.append(
                "<summary>Show general assessment evidence</summary>"
            )
            report.append("")

            for item in general_evidence:
                append_evidence_item(item)

            report.append("</details>")
            report.append("")

    # ---------------------------------------------------------
    # Activity Timeline
    # ---------------------------------------------------------
    report.append("## 8. Activity Timeline")
    report.append("")

    if activities:
        report.append(
            "| Time | Type | Area | Test | Tool | Asset | Title |"
        )
        report.append(
            "|---|---|---|---|---|---|---|"
        )

        for activity in activities:
            asset = asset_by_id.get(activity.asset_id)
            asset_name = (
                asset.value
                if asset
                else display_id(activity.asset_id)
            )

            report.append(
                f"| {activity.created_at} | "
                f"{markdown_cell(activity.activity_type)} | "
                f"{markdown_cell(activity.testing_area or '—')} | "
                f"{markdown_cell(activity.test_type or '—')} | "
                f"{markdown_cell(activity.tool or '—')} | "
                f"`{markdown_cell(asset_name)}` | "
                f"{markdown_cell(activity.title)} |"
            )
    else:
        report.append("No activities recorded.")

    report.append("")

    # ---------------------------------------------------------
    # Footer
    # ---------------------------------------------------------
    report.append("---")
    report.append("")
    report.append(
        "*Generated by VANTA — Virtual Attack & Network Testing Arena.*"
    )
    report.append("")

    report_content = "\n".join(report)

    filename = (
        f"{safe_filename(engagement.name)}_report.md"
    )

    report_path = REPORTS_DIR / filename

    report_path.write_text(
        report_content,
        encoding="utf-8",
    )

    return filename, str(report_path)