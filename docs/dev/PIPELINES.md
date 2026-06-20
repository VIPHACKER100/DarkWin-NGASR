# DARKWIN Pipeline Architecture

## Overview

The Pipeline Engine (`core/pipeline_engine.py`) orchestrates sequential execution of scan phases. Each pipeline is a sequence of `PipelineStep` objects that share context and data as they execute.

## Pipeline Engine (`core/pipeline_engine.py`)

### Core Classes

```python
PipelineStep(name, module_fn, args, phase, depends_on=None)
Pipeline(name, steps, target, scan_id)
```

### Execution Flow

1. Steps are grouped by `phase` number
2. Phases execute in ascending order
3. Within a phase, steps execute in definition order
4. Context (discovered subdomains, endpoints) is passed between phases
5. Errors in one step do not halt the entire pipeline

## Built-in Pipelines

### 1. Recon Pipeline (`pipelines/recon_pipeline.py`)

```
Phase 1: Passive Recon
  ├── Subdomain enumeration (Subfinder, Amass)
  ├── Certificate transparency (CRT.sh)
  ├── DNS records enumeration
  └── WHOIS lookup

Phase 2: Active Recon
  ├── Port scanning
  ├── Technology fingerprinting
  └── Endpoint discovery
```

### 2. Web Vulnerability Pipeline (`pipelines/web_vuln_pipeline.py`)

```
Phase 1: Crawling & Discovery
  ├── Web crawler
  ├── JavaScript analysis
  └── Parameter discovery

Phase 2: Injection Testing
  ├── SQLi / NoSQLi
  ├── Command injection
  ├── SSTI / Template injection
  └── XSS (Reflected/Stored/DOM)

Phase 3: Logic & Config
  ├── CSRF
  ├── CORS misconfiguration
  ├── Open redirect
  ├── SSRF
  └── Security headers audit

Phase 4: File & Server
  ├── LFI / RFI
  ├── File upload bypass
  └── RCE fingerprinting
```

### 3. Full Hunt Pipeline (`pipelines/full_hunt_pipeline.py`)

```
Phase 1: Recon          → ReconPipeline
Phase 2: Intel          → Intelligence gathering
Phase 3: Web Scanning   → WebVulnPipeline
Phase 4: Fuzzing        → Directory + API + Parameter
Phase 5: Network        → Port scan + Service enum
Phase 6: Cloud          → S3/Azure/GCP audit
Phase 7: Exploit        → CVE matching + MSF bridge
Phase 8: Report         → AI-synthesized report generation
```

## Creating a Custom Pipeline

```python
from core.pipeline_engine import Pipeline, PipelineStep
from modules.reconnaissance.subdomain.enumerator import run as sub_enum
from modules.web_scanning.crawler_engine.spider import run as spider

custom_pipeline = Pipeline(
    name="MyCustomPipeline",
    steps=[
        PipelineStep(
            name="Subdomain Enumeration",
            module_fn=sub_enum,
            args=[target, scan_id],
            phase=1
        ),
        PipelineStep(
            name="Web Crawler",
            module_fn=spider,
            args=[target, scan_id],
            phase=2
        ),
    ],
    target=target,
    scan_id=scan_id
)

await custom_pipeline.run()
```

## Context Sharing

Pipelines use a shared context dictionary that accumulates data:

```python
# Step 1 produces
context["subdomains"] = ["admin.target.com", "api.target.com"]

# Step 2 can consume
for sub in context.get("subdomains", []):
    await scan_subdomain(sub)
```

## Error Handling

- Failed steps are logged but do not stop the pipeline
- Steps can declare `depends_on` to skip gracefully if a dependency failed
- The pipeline records `finished_at` and status per step

## Running Pipelines

### CLI
```bash
# Run a specific pipeline
darkwin recon target.com
darkwin scan target.com

# Full autonomous hunt (AI chooses which pipeline to run)
darkwin hunt target.com
```

### Programmatic
```python
from pipelines.recon_pipeline import ReconPipeline
import asyncio

async def run():
    pipeline = ReconPipeline("target.com", "scan-001")
    await pipeline.run()

asyncio.run(run())
```

## Adding a New Pipeline

1. Create `pipelines/my_pipeline.py`
2. Define steps using `PipelineStep`
3. (Optional) Register with `core/agent_loop.py` for AI selection
4. Test with `darkwin <your-pipeline-command>` (if CLI command added)
