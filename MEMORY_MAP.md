# 🧠 DARKWIN Memory Map (Source of Truth)
**Developer**: ARYAN AHIRWAR (VIPHACKER.100)
**Project**: DARKWIN — Next-Gen Automated Security Research Platform
**Version**: 1.0.0 (Elite Upgrade v2.0)

---

## 🏗️ Architecture Overview
DARKWIN is designed as a modular, pipeline-driven security OS. It uses a core engine to orchestrate specialized modules across various security domains.

### 1. Core Engine (`core/`)
- `darkwin.py`: Main entry point with Banner and Legal check.
- `command_router.py`: Click-based CLI handling.
- `pipeline_engine.py`: Manages the execution flow of modules.
- `database.py` & `models.py`: SQLAlchemy-based persistence (PostgreSQL/SQLite).
- `config_manager.py`: Pydantic-based configuration and validation.

### 2. Module Ecosystem (`modules/`)
- **Reconnaissance**: Subdomain, DNS, Whois, Search Engine dorking.
- **Attack Surface**: Asset mapping and API detection.
- **Vulnerability Engine**:
    - **Injection**: SQL, NoSQL (Blind), GraphQL, SSTI.
    - **Cloud**: AWS IAM, Azure Blob, Lambda misconfigs.
- **Reporting**: HTML, Markdown, HackerOne, Bugcrowd, and **Attack Graph Generator** (Mermaid).

### 3. Pipeline Definitions (`pipelines/`)
- `recon_pipeline.py`: Discovery phase.
- `scan_pipeline.py`: Vulnerability detection phase.
- `full_attack_surface_pipeline.py`: End-to-end automation.

---

## 🛡️ Active Modules List (≈70+)
| Category | High-Impact Modules | Status |
| :--- | :--- | :--- |
| **Recon** | `subdomain_enum`, `dns_resolver`, `whois_lookup` | ✅ Active |
| **Injection** | `blind_nosql`, `graphql_tester`, `ssti_optimizer` | ✅ Active |
| **Cloud** | `aws_iam_scanner`, `azure_blob_brute`, `lambda_audit` | ✅ Active |
| **Automation** | `pipeline_engine`, `command_router` | ✅ Active |
| **Reporting** | `attack_graph_generator`, `hackerone_format` | ✅ Active |

---

## 🚀 ROADMAP: The "Elite 500" Goal
- [ ] **Distributed Scanning**: Implement Celery workers for multi-node tasking.
- [ ] **Continuous Monitoring**: Build the `darkwin watch` command.
- [ ] **Exploit Search**: Match technology stacks directly with CVE databases.
- [ ] **Web Dashboard**: Full React/Flask integration for real-time visualization.

---

## 🔐 Security & Ethics
- **LEGAL.md**: Hardcoded acknowledgement required for first run.
- **Scope Enforcer**: `scope.json` validation before any network activity.
- **Developer Attribution**: "ARYAN AHIRWAR (VIPHACKER.100)" must be present in all outputs.

---

*This Memory Map is updated automatically to preserve project integrity.*
