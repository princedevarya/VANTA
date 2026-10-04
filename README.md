# VANTA

# Virtual Attack & Network Testing Arena

> **A portfolio-grade security assessment and VAPT orchestration platform for structured reconnaissance, attack-surface mapping, controlled security testing, evidence collection, finding management, attack-path analysis, and professional reporting.**

VANTA is a Dockerized cybersecurity assessment platform designed around the workflow of a professional penetration tester and vulnerability assessment team.

Instead of being only a collection of security scanners, VANTA is designed to connect the complete assessment lifecycle:

```text
Scope
  ↓
Reconnaissance
  ↓
Asset Discovery
  ↓
Attack Surface Mapping
  ↓
Web / API / Network Testing
  ↓
Finding Validation
  ↓
Evidence Collection
  ↓
Risk Assessment
  ↓
Attack-Path Correlation
  ↓
Remediation
  ↓
Retest
  ↓
Professional Report
# Installation

## Requirements

Before installing VANTA, make sure you have:

- Git
- Docker
- Docker Compose

## 1. Clone the Repository

```bash
git clone https://github.com/princedevarya/VANTA.git
cd VANTA
chmod +x scripts/start-vanta.sh
./scripts/start-vanta.sh

## Updating VANTA

If you already have VANTA installed, update it with:

```bash
./scripts/update-vanta.sh