from dataclasses import dataclass


@dataclass
class FindingCandidate:
    title: str
    description: str
    severity: str
    remediation: str
    confidence: str = "medium"


def detect_findings(
    *,
    testing_area: str | None,
    test_type: str | None,
    output: str,
) -> list[FindingCandidate]:
    """
    Deterministic finding detection.

    Detection creates hypotheses only.
    Validation remains a separate analyst action.
    """

    if not output:
        return []

    text = output.lower()

    candidates: list[FindingCandidate] = []

    if (
        testing_area == "network"
        and test_type in {
            "port_enumeration",
            "service_enumeration",
            "network_configuration",
        }
    ):
        if "open" in text and (
            "externally reachable" in text
            or "exposed services" in text
            or "port 8080" in text
            or "port 8443" in text
        ):
            candidates.append(
                FindingCandidate(
                    title="Potential exposed service",
                    description=(
                        "The assessment evidence indicates that a "
                        "network service may be externally reachable. "
                        "Further validation is required to determine "
                        "whether the exposure is intended and whether "
                        "the service presents a security risk."
                    ),
                    severity="medium",
                    remediation=(
                        "Restrict externally reachable services to "
                        "those required by the application and "
                        "engagement scope. Review firewall and "
                        "network access-control rules."
                    ),
                )
            )

    if (
        testing_area == "web"
        and test_type == "authentication"
    ):
        if (
            "manual validation" in text
            and (
                "brute-force" in text
                or "lockout" in text
                or "mfa" in text
            )
        ):
            candidates.append(
                FindingCandidate(
                    title="Authentication controls require validation",
                    description=(
                        "The authentication assessment identified "
                        "security-sensitive authentication controls "
                        "requiring manual validation."
                    ),
                    severity="informational",
                    remediation=(
                        "Verify MFA, credential policy, account "
                        "lockout, throttling, and brute-force "
                        "resistance."
                    ),
                )
            )

    if (
        testing_area == "web"
        and test_type == "authorization"
    ):
        if (
            "manual validation" in text
            and "authorization" in text
        ):
            candidates.append(
                FindingCandidate(
                    title="Authorization controls require validation",
                    description=(
                        "The authorization assessment identified "
                        "resource and privilege boundaries that "
                        "require manual validation."
                    ),
                    severity="informational",
                    remediation=(
                        "Verify horizontal and vertical authorization "
                        "boundaries for protected resources."
                    ),
                )
            )

    if (
        testing_area == "api"
        and test_type == "object_level_authorization"
    ):
        if (
            "object" in text
            and "cross-user" in text
        ):
            candidates.append(
                FindingCandidate(
                    title="Potential object-level authorization weakness",
                    description=(
                        "The API assessment identified object-level "
                        "authorization boundaries that require "
                        "cross-user validation."
                    ),
                    severity="medium",
                    remediation=(
                        "Enforce server-side authorization for every "
                        "object access and verify that object "
                        "identifiers cannot be used to access another "
                        "user's resources."
                    ),
                )
            )

    if (
        testing_area == "api"
        and test_type == "rate_limiting"
    ):
        if (
            "rate-sensitive" in text
            and "manual validation" in text
        ):
            candidates.append(
                FindingCandidate(
                    title="API rate limiting requires validation",
                    description=(
                        "The API assessment identified endpoints "
                        "where throttling behavior should be "
                        "validated."
                    ),
                    severity="informational",
                    remediation=(
                        "Apply appropriate rate limits to "
                        "authentication, resource-intensive, and "
                        "abuse-sensitive API endpoints."
                    ),
                )
            )

    return candidates