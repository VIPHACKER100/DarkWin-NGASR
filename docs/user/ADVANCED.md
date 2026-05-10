# 🏴‍☠️ DARKWIN-NGASR: Advanced Usage & Optimization
## Developed by ARYAN AHIRWAR (VIPHACKER.100)

This guide is for power users who want to tune DARKWIN-NGASR for maximum efficiency, stealth, and performance in large-scale environments.

---

## 📑 Table of Contents
1. [Stealth Tuning (Ghost Mode)](#-stealth-tuning-ghost-mode)
2. [High-Performance Fuzzing](#-high-performance-fuzzing)
3. [Distributed Scaling (Mesh)](#-distributed-scaling-mesh)
4. [Agentic Reasoning Tuning](#-agentic-reasoning-tuning)
5. [Custom One-Liner Integration](#-custom-one-liner-integration)
6. [Platform Performance Optimization](#-platform-performance-optimization)

---

## 🕵️ Stealth Tuning (Ghost Mode)

The Stealth Engine (`core/stealth.py`) is your best friend when scanning hardened targets.

### Gaussian Jitter
Instead of fixed delays, use `--stealth` to enable randomized delays based on a normal distribution.
```bash
darkwin hunt example.com --stealth
```

### Fingerprint Spoofing
DARKWIN uses `curl-cffi` to mimic specific browser TLS/JA3 fingerprints. You can override the default in `config.yaml`:
```yaml
stealth:
  browser: "chrome_120" # Options: chrome, firefox, safari
```

---

## ⚡ High-Performance Fuzzing

For massive endpoint discovery, combine the power of internal modules with community tools.

### Wordlist Strategy
Always use optimized wordlists. You can download the latest Seclists directly:
```bash
darkwin wordlists --download
```

### Rate Limiting
Prevent WAF bans by tuning your global rate limit in `config.yaml`:
```yaml
rate_limit:
  max_requests_per_second: 10
  burst_size: 5
```

---

## 🌐 Distributed Scaling (Mesh)

Deploying a mesh allows you to distribute the scan load across multiple IPs.

### Node Configuration
Each node should have a unique `NODE_ID` in its `.env` file but share the same `REDIS_URL`.

### Monitoring the Mesh
Use the CLI to monitor node health and task distribution:
```bash
darkwin mesh
```

---

## 🤖 Agentic Reasoning Tuning

The AI Reasoning Engine can be tuned for different goals.

### Reasoning Depth
For simple targets, use `--max-steps 5` to save API costs. For complex internal networks, use `--max-steps 30`.
```bash
darkwin hunt internal.corp --max-steps 30
```

### Model Selection
Switch models based on your needs. Use `gpt-4-turbo` for complex reasoning or `gpt-3.5-turbo` for rapid, low-cost assessments.

---

## 🏴‍☠️ Custom One-Liner Integration

DARKWIN allows you to run complex bug bounty one-liners natively.

### The One-Liner Adapter
You can add your favorite one-liners to `pipelines/one_liners.py`. These will be automatically picked up by the AI during a hunt.

Example:
```bash
# Manually run a specialized one-liner through the adapter
darkwin run-one-liner "subfinder -d target.com | httpx | nuclei"
```

---

## 🚀 Platform Performance Optimization

### Database Maintenance
Large scan histories can slow down the dashboard. Regularly purge old data:
```bash
darkwin clean --logs --temp
```

### Memory Management
When running with high concurrency, ensure your system has enough file descriptors:
```bash
ulimit -n 65535
```

---
<div align="center">
<b>Master the Shadows with DARKWIN-NGASR</b><br/>
© 2026 ARYAN AHIRWAR (VIPHACKER.100)
</div>
