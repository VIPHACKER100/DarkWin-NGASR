# DARKWIN Hunting Workflows

## 1. Quick Reconnaissance

Quickly enumerate subdomains, endpoints, and technology stack:

```bash
darkwin recon target.com
```

Follow with:
```bash
darkwin history --limit 5                              # Check results
darkwin reports <scan_id> --format md                  # Generate summary
```

## 2. Full Autonomous Hunt

Let the AI agent plan and execute a complete assessment:

```bash
# Standard depth (5 reasoning steps) — good for small targets
darkwin hunt target.com

# Deep reasoning (30 steps) — for complex targets
darkwin hunt target.com --max-steps 30

# With stealth evasion — for WAF-protected targets
darkwin hunt target.com --stealth --proxy
```

The agent will: recon → analyze → select modules → verify findings → report.

## 3. Continuous Monitoring

Monitor a target for changes over time:

```bash
# Initial full reconnaissance
darkwin hunt target.com --max-steps 15

# Watch mode for ongoing changes
darkwin watch target.com

# Schedule weekly scans
darkwin schedule --add "hunt target.com weekly"
```

## 4. Bug Bounty Workflow

High-efficiency workflow for bug bounty programs:

```bash
# Step 1: Passive reconnaissance
darkwin recon target.com

# Step 2: JavaScript secrets extraction
# (integrated into the full scan pipeline)

# Step 3: Targeted vulnerability scanning
darkwin scan target.com

# Step 4: Generate professional report
darkwin reports --open        # List and open latest report
```

## 5. Distributed Mesh Scanning

For large scope with multiple attack origins:

**On master node:**
```bash
docker-compose up -d
darkwin targets --add target.com
```

**On worker nodes:**
```bash
# Set REDIS_URL to master's IP in .env
./setup.sh && source .venv/bin/activate
# Worker auto-registers with master via Redis
```

**Monitor:**
```bash
darkwin mesh          # View connected nodes
darkwin hunt target.com --max-steps 50  # Distribute across mesh
```

## 6. Stealth-First Approach

For hardened targets with WAF/IDS:

```bash
# Configure stealth in config.yaml
#   stealth.enabled: true
#   stealth.browser: "chrome_120"
#   stealth.jitter_range: [3, 10]

darkwin hunt target.com --stealth --proxy

# Monitor evasion status
darkwin proxy          # Check proxy pool health
darkwin logs --tail 20 # Verify no blocks detected
```

## 7. Pipeline Chaining

Run specific phases independently:

```bash
# Phase 1: Recon only
darkwin recon target.com

# Phase 2: Web vulnerability scan
darkwin scan target.com

# Phase 3: Fuzzing for hidden endpoints
darkwin fuzz target.com

# Phase 4: Cloud infrastructure audit
darkwin cloud target.com
```

## 8. Full Audit + Report

Complete assessment from start to professional report:

```bash
# Full autonomous hunt
darkwin hunt target.com --max-steps 20

# Generate all report formats
darkwin reports                          # List reports
darkwin report <scan_id> --format pdf    # Executive PDF
darkwin report <scan_id> --format html   # Interactive HTML
darkwin report <scan_id> --format md     # Markdown summary
```

## Quick Reference Card

```bash
# Most common commands
darkwin hunt <target>        # Autonomous AI hunting
darkwin shell                # Interactive REPL
darkwin modules              # List all modules
darkwin targets --list       # View scope
darkwin history              # Recent scans
darkwin reports              # Generated reports
darkwin doctor --fix         # Self-healing diagnostics
darkwin logs --tail 20       # Recent logs
```
