# 🚀 DARKWIN-NGASR Advanced Command Guide

This guide covers advanced CLI usage, complex workflows, and power-user configurations for the DARKWIN-NGASR platform.

---

## 🧠 Autonomous Hunting (`hunt`)

The `hunt` command is the core of DARKWIN's agentic intelligence.

### Advanced Reasoning Control
```bash
# Increase reasoning depth for complex targets (default is 5)
darkwin hunt example.com --max-steps 15

# Use a specific scope policy for legal compliance
darkwin hunt example.com --scope-file policies/bugbounty.json
```

---

## 🛠️ Management & Operations

### Target Scope Management
```bash
# Add multiple targets to the database
darkwin targets --add alpha.com
darkwin targets --add beta.com

# Audit your target surface
darkwin targets
```

### Scan History & Auditing
```bash
# View the last 100 scans
darkwin history --limit 100

# Search logs for a specific finding (e.g., XSS)
darkwin logs --search "XSS"
```

---

## 📦 Tactical Assets

### Wordlist Management
```bash
# Download industry-standard recon wordlists
darkwin wordlists --download

# List local wordlist inventory
darkwin wordlists
```

### Payload Injection
```bash
# List all available exploit categories
darkwin payloads

# View all RCE payloads
darkwin payloads --type rce
```

---

## 📸 Evidence & Reporting

### Evidence Auditing
```bash
# View all screenshots from a specific scan
darkwin screenshots --scan-id 5fe548ca-b022...

# Instantly open the latest verified finding
darkwin screenshots --open
```

### AI Reporting
```bash
# Generate an executive PDF report
darkwin report <scan_id> --format pdf

# Export raw findings to Markdown for documentation
darkwin report <scan_id> --format md
```

---

## ⚙️ System & Maintenance

### Configuration & Health
```bash
# View current config (secrets are auto-masked)
darkwin config --view

# Interactive configuration editing
darkwin config --edit

# Run deep diagnostics and self-healing
darkwin doctor --fix
```

### Platform Purge
```bash
# Clean everything (logs, screenshots, temp files)
darkwin clean --all

# Clean only temporary caches
darkwin clean --temp
```

---

## 📅 Automation

### Task Scheduling
```bash
# Schedule a weekly autonomous hunt
darkwin schedule --add "hunt example.com weekly"

# List all active recurring missions
darkwin schedule --list
```

---

## 🛠️ Troubleshooting Utility
```bash
# Launch the interactive troubleshooting wizard
darkwin troubleshoot

# Run a quick diagnostic check
darkwin troubleshoot --check
```

---
<div align="center">
<b>DARKWIN-NGASR | Autonomous · Distributed · Stealthy</b>
</div>
