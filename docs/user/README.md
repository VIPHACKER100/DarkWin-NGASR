# 🛡️ DARKWIN-NGASR: The Ultimate User & Setup Guide
## Developed by ARYAN AHIRWAR (VIPHACKER.100)

Welcome to the comprehensive guide for **DARKWIN-NGASR**, the Next-Gen Autonomous Security Researcher. This document provides step-by-step instructions for setting up the platform, configuring your environment, and mastering the CLI.

---

## 📑 Table of Contents
1. [Prerequisites](#-prerequisites)
2. [Installation Guide](#-installation-guide)
3. [Configuration](#-configuration)
4. [External Security Tools](#-external-security-tools)
5. [Getting Started (CLI)](#-getting-started-cli)
6. [Autonomous Hunting (Agentic Mode)](#-autonomous-hunting-agentic-mode)
7. [Distributed Mesh Setup](#-distributed-mesh-setup)
8. [Dashboard & Visualization](#-dashboard--visualization)
9. [Troubleshooting & Diagnostics](#-troubleshooting--diagnostics)
10. [Legal Disclaimer](#-legal-disclaimer)

---

## 📋 Prerequisites

Before installing DARKWIN-NGASR, ensure your system meets the following requirements:

### Operating System
- **Recommended**: Kali Linux, Parrot OS, Ubuntu, or Debian.
- **Supported**: macOS, Windows (via PowerShell or WSL2).

### Core Dependencies
- **Python 3.11+**: The engine is built on modern Python features.
- **Node.js 20+**: Required for the Next.js dashboard.
- **Docker & Docker Compose**: Required for running the database, Redis, and dashboard services.
- **Go (Golang) 1.21+**: Required for installing many external security tools.
- **Redis 7+**: Used for the mesh registry and task queuing.
- **PostgreSQL 15+**: Primary persistent storage for scan results.

---

## 🚀 Installation Guide

### 1. Clone the Repository
```bash
git clone https://github.com/VIPHACKER100/DarkWin-NGASR.git
cd DarkWin-NGASR
```

### 2. Run the Setup Script
The setup script creates a virtual environment and installs all Python dependencies in isolation.

**Linux / macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows (PowerShell):**
```powershell
.\setup.ps1
```

### 3. Activate the Virtual Environment
**Always** activate the virtual environment before running `darkwin` commands.

**Linux / macOS:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Verify Installation
Run the "doctor" utility to check if your environment is healthy.
```bash
darkwin doctor
```

---

## ⚙️ Configuration

DARKWIN-NGASR uses a central `config.yaml` and `.env` for configuration.

### 1. The Interactive Setup Wizard (Recommended)
The easiest way to configure the platform is to use the interactive wizard:
```bash
darkwin setup
```
This wizard will guide you through setting up:
- **Database Connection** (Postgres/SQLite)
- **Redis Connection** (For mesh and tasks)
- **API Keys** (OpenAI, Shodan, GitHub)
- **AI Model Selection** (gpt-4o, etc.)

### 2. Manual Configuration
Alternatively, you can copy the example files and edit them manually:
```bash
cp config.yaml.example config.yaml
cp .env.example .env
```

Open `config.yaml` to add your keys:
```yaml
ai:
  openai_api_key: "sk-..."
  openai_model: "gpt-4o"

api_keys:
  shodan: "your-shodan-key"
```

---

## 🛠️ External Security Tools

While DARKWIN has internal modules, it reaches peak performance when integrated with industry-standard tools.

### Automated Tool Installation
Run the doctor with the `--fix` flag to attempt an automated installation of missing tools via Go:
```bash
darkwin doctor --fix
```

### Manual Tool Installation (via Makefile)
```bash
make setup-tools
```

### Recommended Tools List:
- `nmap`, `subfinder`, `httpx`, `nuclei`, `ffuf`, `amass`, `katana`, `sqlmap`, `dalfox`, `masscan`, `gau`, `waybackurls`.

---

## 🎯 Getting Started (CLI)

### 1. The Interactive Shell
For the best experience, use the interactive REPL with tab-completion.
```bash
darkwin shell
```

### 2. Basic Hunting
Start an autonomous hunt for a target domain.
```bash
darkwin hunt example.com
```

### 3. Managing Targets
Add targets to your persistent scope.
```bash
darkwin targets --add scope.com
darkwin targets --list
```

### 4. Generating Reports
After a scan is complete, generate a professional report.
```bash
# Get the scan ID from 'darkwin history'
darkwin history
darkwin report <scan_id> --format pdf
```

---

## 🤖 Autonomous Hunting (Agentic Mode)

The `hunt` command is the heart of DARKWIN. It uses an **Agentic Reasoning Loop** to make decisions.

### How it works:
1. **Analyze**: AI looks at the target's open ports and technology stack.
2. **Plan**: AI selects the best modules to run next (e.g., "Target uses WordPress, running WPScan").
3. **Execute**: The platform runs the selected tools.
4. **Learn**: AI analyzes the results and decides the next move until the target is exhausted.

### Advanced Tuning:
```bash
# Deeper reasoning for complex targets
darkwin hunt example.com --max-steps 20

# Force stealth mode (proxy rotation + jitter)
darkwin hunt example.com --proxy --stealth
```

---

> For a complete Docker deployment guide (production scaling, volume management, troubleshooting), see [Docker Deployment Guide](DOCKER.md).
> For detailed dashboard setup and feature walkthrough, see [Dashboard Guide](DASHBOARD.md).
> For common hunting patterns and recipes, see [Hunting Workflows](WORKFLOWS.md).

## 🌐 Distributed Mesh Setup

DARKWIN can scale horizontally across multiple servers.

1. **Master Node**: Run the full stack.
   ```bash
   docker-compose up -d
   ```
2. **Worker Node**: Install DARKWIN on a remote server and point the `REDIS_URL` in `.env` to the Master Node's IP.
3. **Verify**: Check the mesh status from the master.
   ```bash
   darkwin mesh
   ```

---

## 🎨 Dashboard & Visualization

Launch the full-stack orchestration to access the web HUD.

1. **Start Services**:
   ```bash
   docker-compose up -d --build
   ```
2. **Access URL**:
   - **Dashboard**: `http://localhost:3000`
   - **API**: `http://localhost:5000`

### Features:
- **3D Neural Map**: Visualize the attack surface in 3D.
- **Live Logs**: Watch findings happen in real-time.
- **Evidence Vault**: View screenshots and raw request/response data.

---

## 🔧 Troubleshooting & Diagnostics

If you encounter issues, use the following tools:

- **Self-Healing**: `darkwin doctor --fix` (Fixes permissions, venv, and missing tools).
- **Environment Check**: `darkwin troubleshoot` (Interactive guide).
- **Log Inspection**: `darkwin logs --tail 50`.

### Common Fixes:
- **`ModuleNotFoundError`**: Ensure you ran `source .venv/bin/activate`.
- **`Redis Connection Error`**: Ensure `docker-compose up -d redis` is running.
- **`Permission Denied`**: Run `darkwin doctor --fix`.

---

## ⚖️ Legal Disclaimer

**IMPORTANT**: This tool is for **authorized security research** and **educational purposes only**. Unauthorized scanning of targets is illegal and unethical. The author, **ARYAN AHIRWAR (VIPHACKER.100)**, is not responsible for any misuse or damage caused by this software. Use responsibly.

---
<div align="center">
<b>DARKWIN-NGASR | Autonomous · Distributed · Stealthy</b><br/>
© 2026 ARYAN AHIRWAR
</div>
