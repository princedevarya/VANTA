# VANTA

### Virtual Attack & Network Testing Arena

> **A portfolio-grade security assessment and VAPT orchestration platform for controlled, repeatable offensive-security testing.**

<p align="center">

**Scope → Recon → Discovery → Testing → Evidence → Findings → Attack Paths → Reporting**

</p>

---

## ⚡ What is VANTA?

**VANTA (Virtual Attack & Network Testing Arena)** is a security assessment platform designed to model how a professional **Vulnerability Assessment and Penetration Testing (VAPT)** engagement is performed.

Instead of treating security testing as a collection of disconnected scanners, VANTA organizes the assessment around an actual security workflow:

```text
                    ┌──────────────────────┐
                    │       ENGAGEMENT     │
                    │       & SCOPE        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │        RECON         │
                    │ DNS / Subdomains     │
                    │ Technologies         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   ASSET DISCOVERY    │
                    │ Domains / Hosts / IPs │
                    │ Services / Endpoints │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      TESTING         │
                    │ Web / API / Network  │
                    │ Controlled Execution │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      EVIDENCE        │
                    │ Output / Artifacts   │
                    │ Traceability         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     FINDINGS         │
                    │ Risk / Validation    │
                    │ Remediation          │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    ATTACK PATHS      │
                    │ Correlation / Impact │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       REPORT         │
                    │ Assessment Results   │
                    └──────────────────────┘
```

The goal is not to build "another vulnerability scanner."

The goal is to build a **security assessment workspace** where reconnaissance, testing, evidence, findings, and attack-path reasoning become connected parts of one assessment.

---

## 🎯 Why VANTA?

Traditional security tools often produce isolated output:

```text
Scanner A → output
Scanner B → output
Scanner C → output
```

The security engineer then has to manually correlate everything.

VANTA is designed around:

```text
Target
  ↓
Asset
  ↓
Recon
  ↓
Attack Surface
  ↓
Security Test
  ↓
Tool Execution
  ↓
Evidence
  ↓
Finding
  ↓
Risk
  ↓
Attack Path
  ↓
Report
```

This makes the platform useful for demonstrating the **complete assessment lifecycle**, rather than simply demonstrating that several security tools can be executed.

---

# 🧭 Core Capabilities

## Engagement Management

Create and manage security assessments with:

- Engagement identity
- Client information
- Assessment status
- Description
- Scope
- Target assets
- Assessment activity history

---

## Scope Management

VANTA treats scope as a first-class security concept.

Assets can be explicitly included or excluded from an assessment.

```text
IN SCOPE
├── example.com
├── api.example.com
└── 10.10.10.20

OUT OF SCOPE
├── admin.example.com
└── internal.example.com
```

This allows testing workflows to maintain a clear boundary between authorized targets and excluded assets.

---

# 🔎 Reconnaissance

VANTA provides an orchestration layer for reconnaissance tooling.

### DNS Enumeration

Uses `dig` to retrieve DNS information.

Example:

```text
Target
  ↓
dig
  ↓
DNS records
  ↓
Evidence
```

### Subdomain Discovery

Uses **Subfinder** for passive subdomain discovery.

```text
Domain
  ↓
Subfinder
  ↓
Discovered subdomains
  ↓
Asset inventory
```

### Technology Discovery

Uses **HTTPX** to identify HTTP services and technology information.

```text
Target
  ↓
HTTPX
  ↓
HTTP service
  ↓
Technology metadata
```

---

# 🌐 Web Security Testing

VANTA integrates web reconnaissance into the assessment workflow.

### Endpoint Discovery

Uses **Katana** for controlled web crawling and endpoint discovery.

```text
Web Target
    ↓
  Katana
    ↓
Endpoints
    ↓
Endpoint Inventory
    ↓
Evidence
```

Discovered endpoints can be persisted into the VANTA endpoint inventory for later testing and analysis.

---

# 🖧 Network Security Testing

VANTA integrates **Nmap** for controlled network assessment.

Current testing capabilities include:

### Port Enumeration

```text
Nmap
 ↓
Open ports
 ↓
Service inventory
```

### Service Enumeration

```text
Nmap -sV
 ↓
Service detection
 ↓
Version information
```

### Network Configuration Observation

VANTA can execute a controlled Nmap configuration-oriented scan and preserve the resulting evidence.

Example output:

```text
22/tcp    open  ssh
80/tcp    open  http
443/tcp   open  ssl/http
2222/tcp  open  ssh
3306/tcp  open  mysql
```

The result is associated with:

- Engagement
- Asset
- Testing area
- Test type
- Tool execution
- Evidence

---

# 🧪 Testing Architecture

VANTA separates **what is being tested** from **how the test is executed**.

```text
TESTING TAXONOMY
       │
       ├── Recon
       │    ├── DNS
       │    ├── Subdomain Discovery
       │    └── Technology Discovery
       │
       ├── Network
       │    ├── Port Enumeration
       │    ├── Service Enumeration
       │    └── Network Configuration
       │
       └── Web
            └── Endpoint Discovery
                    │
                    ▼
             Execution Engine
                    │
                    ▼
               Tool Adapter
                    │
                    ▼
                 Tool
                    │
                    ▼
                 Parser
                    │
                    ▼
              VANTA Evidence
```

This adapter-based design allows additional security tools to be integrated without redesigning the entire application.

---

# 🧩 Tool Adapter Architecture

VANTA uses adapters to isolate external security tools from the core application.

Conceptually:

```python
ToolAdapter
    │
    ├── NmapAdapter
    ├── SubfinderAdapter
    ├── HTTPXAdapter
    ├── KatanaAdapter
    └── DnsAdapter
```

Each adapter is responsible for:

1. Building the command
2. Executing the tool
3. Capturing stdout/stderr
4. Returning structured execution metadata
5. Passing results to the appropriate parser

This provides a clean boundary between:

```text
VANTA
  ↕
Tool Adapter
  ↕
External Security Tool
```

---

# 📦 Parsing & Normalization

Raw tool output is not treated as the final data model.

VANTA converts tool output into structured information.

Example:

```text
Raw Nmap Output
       ↓
     Parser
       ↓
Structured Services
       ↓
Asset / Service Inventory
       ↓
Evidence
```

This makes information generated by different tools usable by the same assessment system.

---

# 🧾 Evidence & Traceability

Security testing is only useful when results can be traced back to the action that produced them.

VANTA therefore maintains relationships between:

```text
Engagement
     │
     ├── Asset
     │
     ├── Activity
     │      │
     │      └── Tool Execution
     │
     └── Evidence
            │
            └── Finding
```

This allows an assessor to answer:

> **What happened, against which asset, using which tool, and what evidence supports the result?**

---

# 🧠 Findings

VANTA provides a foundation for structured security findings.

A finding can be associated with:

- Engagement
- Asset
- Evidence
- Severity
- Status
- Validation state
- Description
- Remediation information

The intended lifecycle is:

```text
Hypothesis
    ↓
Validation
    ↓
Confirmed Finding
    ↓
Risk Assessment
    ↓
Remediation
    ↓
Retest
```

---

# 🕸️ Attack-Path Correlation

One of the long-term goals of VANTA is moving beyond isolated vulnerabilities.

Instead of:

```text
Finding A
Finding B
Finding C
```

VANTA is designed to model:

```text
Initial Access
      ↓
Exposed Service
      ↓
Weak Configuration
      ↓
Application Exposure
      ↓
Privilege / Impact
```

This enables security findings to be interpreted as part of an **attack path**, rather than merely a list of independent scanner results.

---

# 📊 Platform Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                       VANTA UI                          │
│                   React + TypeScript                    │
└──────────────────────────┬──────────────────────────────┘
                           │
                           │ HTTP / REST
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                      │
│                                                         │
│  API Layer                                              │
│  ├── Engagements                                        │
│  ├── Scopes                                             │
│  ├── Assets                                             │
│  ├── Activities                                         │
│  ├── Evidence                                           │
│  ├── Findings                                           │
│  ├── Endpoints                                          │
│  └── Tool Events                                        │
│                                                         │
│  Services                                               │
│  ├── Orchestrator                                       │
│  ├── Asset Discovery                                    │
│  ├── Endpoint Inventory                                 │
│  ├── Service Inventory                                  │
│  ├── Parsers                                            │
│  └── Tool Adapters                                      │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Security Tools                      │
│                                                         │
│    Nmap     Subfinder     HTTPX     Katana     dig      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    SQLite Database                      │
│                                                         │
│ Engagements │ Assets │ Activities │ Evidence │ Findings │
└─────────────────────────────────────────────────────────┘
```

---

# 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript |
| Build Tool | Vite |
| Backend | FastAPI |
| Language | Python |
| ORM | SQLAlchemy |
| Database | SQLite |
| Reverse Proxy | Nginx |
| Containerization | Docker / Docker Compose |
| Network Testing | Nmap |
| Subdomain Discovery | Subfinder |
| HTTP Recon | HTTPX |
| Web Crawling | Katana |
| DNS Enumeration | dig / DNS utilities |
| Tooling | Go + Python |

---

# 🚀 Quick Start

## Prerequisites

You only need:

- Git
- Docker
- Docker Compose

The security tools and application dependencies are intended to run inside the VANTA containers.

---

## Clone

```bash
git clone https://github.com/princedevarya/VANTA.git
cd VANTA
```

---

## Start VANTA

```bash
docker compose up --build
```

Once the containers are running, open the frontend URL exposed by the Docker Compose configuration.

---

## Run in Background

```bash
docker compose up --build -d
```

View logs:

```bash
docker compose logs -f
```

Stop VANTA:

```bash
docker compose down
```

---

# 🔧 Development

To inspect running containers:

```bash
docker compose ps
```

Backend logs:

```bash
docker compose logs -f backend
```

Frontend logs:

```bash
docker compose logs -f frontend
```

Rebuild from scratch:

```bash
docker compose down
docker compose build --no-cache
docker compose up
```

---

# 🧪 Example Assessment Workflow

A typical VANTA assessment can follow:

```text
1. Create Engagement
        ↓
2. Define Scope
        ↓
3. Add Target
        ↓
4. Discover Assets
        ↓
5. Perform DNS Recon
        ↓
6. Discover Subdomains
        ↓
7. Identify Technologies
        ↓
8. Enumerate Network Services
        ↓
9. Discover Web Endpoints
        ↓
10. Validate Findings
        ↓
11. Collect Evidence
        ↓
12. Correlate Attack Paths
        ↓
13. Assess Risk
        ↓
14. Remediate
        ↓
15. Retest
        ↓
16. Generate Report
```

---

# 🔐 Security Model

VANTA is designed for **authorized security testing and controlled assessment environments**.

Use VANTA only against:

- Systems you own
- Systems you have explicit authorization to assess
- Dedicated security labs
- CTF environments
- Purpose-built vulnerable infrastructure
- Authorized bug-bounty targets within their published scope

Do **not** use the platform to scan or test systems without permission.

VANTA is an orchestration and assessment platform; authorization and scope remain the responsibility of the security operator.

---

# 🧱 Project Structure

```text
VANTA/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   │       ├── adapters/
│   │       ├── parsers/
│   │       ├── orchestrator/
│   │       └── detection/
│   │
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── nginx/
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

# 🗺️ Roadmap

### Phase I — Foundation

- [x] Engagement management
- [x] Scope management
- [x] Asset inventory
- [x] Activity tracking
- [x] Evidence storage
- [x] Finding model
- [x] Tool adapter architecture
- [x] Dockerized deployment

### Phase II — Reconnaissance

- [x] DNS enumeration
- [x] Subdomain discovery
- [x] Technology discovery
- [x] Network service discovery
- [x] Web endpoint discovery
- [x] Endpoint inventory

### Phase III — Assessment Intelligence

- [ ] Advanced finding detection
- [ ] Finding validation workflow
- [ ] Risk scoring
- [ ] Evidence-to-finding relationships
- [ ] Attack-path correlation
- [ ] Asset relationship graph

### Phase IV — Reporting

- [ ] Professional VAPT report generation
- [ ] Executive summary
- [ ] Technical findings
- [ ] Risk matrix
- [ ] Remediation tracking
- [ ] Retest workflow

### Phase V — Platform Expansion

- [ ] API security testing workflows
- [ ] Authentication testing
- [ ] Cloud assessment workflows
- [ ] Credential exposure detection
- [ ] Advanced asset correlation
- [ ] Distributed tool execution
- [ ] Assessment comparison
- [ ] Historical attack-surface tracking

---

# 🧠 Design Philosophy

VANTA is built around five principles:

### 01 — Scope First

Every assessment begins with an explicit target and scope.

### 02 — Evidence Over Assumptions

Tool output should become traceable assessment evidence.

### 03 — Structured Data Over Raw Output

Security-tool output should be parsed into reusable security objects.

### 04 — Correlation Over Scanner Noise

The platform should help an assessor understand relationships between assets, services, endpoints, and findings.

### 05 — Repeatable Assessments

A security assessment should be reproducible, auditable, and capable of being retested.

---

# 🤝 Contributing

Contributions are welcome.

A typical contribution workflow:

```bash
git clone https://github.com/princedevarya/VANTA.git
cd VANTA

git checkout -b feature/YOUR-FEATURE

# Make your changes

git add .
git commit -m "feat: describe your change"
git push origin feature/YOUR-FEATURE
```

Then open a Pull Request.

---

# 📌 Project Status

**VANTA is under active development.**

The current implementation provides a functional foundation for:

- Engagement management
- Scope management
- Asset discovery
- DNS reconnaissance
- Subdomain discovery
- Technology discovery
- Network enumeration
- Network configuration observation
- Web endpoint discovery
- Tool execution
- Evidence collection
- Endpoint inventory
- Finding management

The platform is continuously evolving toward a complete professional security-assessment workflow.

---

# 👨‍💻 Author

**Prince Arya**

Cybersecurity / VAPT / Pentesting

Building VANTA as a practical security-engineering project focused on understanding and automating real-world assessment workflows.

---

# ⭐ Support the Project

If VANTA is useful or interesting to you:

- ⭐ Star the repository
- 🐛 Report bugs
- 💡 Open feature requests
- 🔧 Submit improvements
- 🔀 Open pull requests

---

## ⚠️ Responsible Use

VANTA is intended for **authorized security assessment, education, research, and controlled laboratory environments**.

The author is not responsible for misuse of the software.

**Always obtain authorization before testing systems you do not own.**

---

<p align="center">

### VANTA

**Virtual Attack & Network Testing Arena**

`Recon • Attack Surface • Testing • Evidence • Findings • Attack Paths`

</p>
