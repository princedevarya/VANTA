from app.services.adapters.base import ToolAdapter, ToolResult


class MockAdapter(ToolAdapter):
    name = "mock"

    SUPPORTED_TESTS = {
        "dns",
        "subdomain_discovery",
        "technology_discovery",
        "port_enumeration",
        "service_enumeration",
        "network_configuration",
        "authentication",
        "authorization",
        "session_management",
        "input_validation",
        "business_logic",
        "object_level_authorization",
        "rate_limiting",
    }

    async def run(
        self,
        target: str,
        test_type: str = "service_enumeration",
    ) -> ToolResult:
        if test_type not in self.SUPPORTED_TESTS:
            raise ValueError(
                f"Mock adapter does not support testing type: {test_type}"
            )

        if test_type == "dns":
            command = f"mock dns {target}"
            output = (
                f"Mock DNS assessment for {target}\n"
                "\n"
                "DNS records:\n"
                f"A      {target}        93.184.216.34\n"
                f"AAAA   {target}        2001:db8::1\n"
                f"MX     {target}        mail.{target}\n"
                f"NS     {target}        ns1.{target}\n"
                f"NS     {target}        ns2.{target}\n"
                "\n"
                "DNS assessment completed.\n"
            )

        elif test_type == "subdomain_discovery":
            command = f"mock subdomain_discovery {target}"
            output = (
                f"Mock subdomain discovery for {target}\n"
                "\n"
                "Discovered subdomains:\n"
                f"SUBDOMAIN api.{target}\n"
                f"SUBDOMAIN app.{target}\n"
                f"SUBDOMAIN admin.{target}\n"
                "\n"
                "Subdomain discovery completed.\n"
            )

        elif test_type == "technology_discovery":
            command = f"mock technology_discovery {target}"
            output = (
                f"Mock technology discovery for {target}\n"
                "\n"
                "Discovered technologies:\n"
                "TECHNOLOGY nginx web_server\n"
                "TECHNOLOGY React frontend\n"
                "TECHNOLOGY FastAPI backend\n"
                "TECHNOLOGY Python runtime\n"
                "\n"
                "Technology discovery completed.\n"
            )

        elif test_type == "authentication":
            command = f"mock authentication {target}"
            output = (
                f"Mock authentication assessment for {target}\n"
                "\n"
                "Authentication checks:\n"
                "- Login endpoint identified.\n"
                "- Authentication mechanism identified.\n"
                "- Invalid credential handling reviewed.\n"
                "- Session establishment observed.\n"
                "- Authentication workflow requires manual validation "
                "for credential, MFA, lockout, and brute-force controls.\n"
                "\n"
                "Authentication assessment completed.\n"
            )

        elif test_type == "authorization":
            command = f"mock authorization {target}"
            output = (
                f"Mock authorization assessment for {target}\n"
                "\n"
                "Authorization checks:\n"
                "- Protected resource identified.\n"
                "- Unauthenticated access boundary reviewed.\n"
                "- User-to-resource authorization boundary reviewed.\n"
                "- Privilege-based access control reviewed.\n"
                "- Direct object access requires manual validation "
                "for horizontal and vertical authorization controls.\n"
                "\n"
                "Authorization assessment completed.\n"
            )

        elif test_type == "session_management":
            command = f"mock session_management {target}"
            output = (
                f"Mock session management assessment for {target}\n"
                "\n"
                "Session management checks:\n"
                "- Session establishment reviewed.\n"
                "- Session cookie attributes reviewed.\n"
                "- Session expiration behavior reviewed.\n"
                "- Session invalidation after logout reviewed.\n"
                "- Session fixation and token lifecycle require manual "
                "validation.\n"
                "\n"
                "Session management assessment completed.\n"
            )

        elif test_type == "input_validation":
            command = f"mock input_validation {target}"
            output = (
                f"Mock input validation assessment for {target}\n"
                "\n"
                "Input validation checks:\n"
                "- User-controlled input locations identified.\n"
                "- Server-side validation behavior reviewed.\n"
                "- Boundary and malformed input handling reviewed.\n"
                "- Encoding and canonicalization behavior reviewed.\n"
                "- Injection resistance requires manual validation.\n"
                "\n"
                "Input validation assessment completed.\n"
            )

        elif test_type == "business_logic":
            command = f"mock business_logic {target}"
            output = (
                f"Mock business logic assessment for {target}\n"
                "\n"
                "Business logic checks:\n"
                "- Primary application workflow identified.\n"
                "- State transitions reviewed.\n"
                "- Workflow sequencing reviewed.\n"
                "- Client-controlled workflow parameters reviewed.\n"
                "- Business rule bypass requires manual validation.\n"
                "\n"
                "Business logic assessment completed.\n"
            )

        elif test_type == "object_level_authorization":
            command = f"mock object_level_authorization {target}"
            output = (
                f"Mock API object-level authorization assessment for {target}\n"
                "\n"
                "Object-level authorization checks:\n"
                "- API object identifiers identified.\n"
                "- Object access boundaries reviewed.\n"
                "- Cross-user object access requires validation.\n"
                "- Horizontal privilege boundaries reviewed.\n"
                "- Vertical privilege boundaries reviewed.\n"
                "\n"
                "Object-level authorization assessment completed.\n"
            )

        elif test_type == "rate_limiting":
            command = f"mock rate_limiting {target}"
            output = (
                f"Mock API rate limiting assessment for {target}\n"
                "\n"
                "Rate limiting checks:\n"
                "- Candidate rate-sensitive endpoints identified.\n"
                "- Request throttling behavior reviewed.\n"
                "- Response behavior under repeated requests reviewed.\n"
                "- Authentication and resource-specific limits require "
                "manual validation.\n"
                "\n"
                "Rate limiting assessment completed.\n"
            )

        elif test_type == "service_enumeration":
            command = f"mock scan {target}"
            output = (
                f"Mock scan completed for {target}\n"
                "PORT 80/tcp open http\n"
                "PORT 443/tcp open https\n"
            )

        elif test_type == "port_enumeration":
            command = f"mock port_enumeration {target}"
            output = (
                f"Mock port enumeration completed for {target}\n"
                "PORT 80/tcp open http\n"
                "PORT 443/tcp open https\n"
            )

        else:
            command = f"mock network_configuration {target}"
            output = (
                f"Mock network configuration assessment for {target}\n"
                "\n"
                "Exposed services:\n"
                "80/tcp   open   http\n"
                "443/tcp  open   https\n"
                "\n"
                "Configuration review:\n"
                "- HTTP service is externally reachable on TCP/80.\n"
                "- HTTPS service is externally reachable on TCP/443.\n"
                "- Service exposure requires configuration review.\n"
                "\n"
                "Network configuration assessment completed.\n"
            )

        return ToolResult(
            tool=self.name,
            command=command,
            output=output,
            return_code=0,
        )