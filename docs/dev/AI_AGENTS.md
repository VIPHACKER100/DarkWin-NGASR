# DARKWIN AI Agent Architecture

## Overview

DARKWIN uses a multi-agent orchestration system where an AI-driven reasoning loop acts as the "brain," making tactical decisions about what to scan next. This mimics the decision-making process of a human security researcher.

## Core Components

### 1. Agentic Loop (`core/agent_loop.py`)

The main orchestration loop that controls autonomous hunts.

```
while steps_remaining:
    1. OBSERVE  — Gather current state (findings, ports, tech stack)
    2. REASON   — Send context to LLM with available module catalog
    3. DECIDE   — AI returns JSON: {next_module, reasoning, priority}
    4. EXECUTE  — Run selected module, record findings
    5. VERIFY   — Auto-verify any critical findings
    6. REPEAT   — Continue until max steps or no more attack surface
```

### 2. Multi-Step Reasoning (`ai/multi_step_reasoning.py`)

Abstracts different AI backends behind a common interface:

```python
class ReasoningBackend:
    async def plan_next_step(context: dict) -> dict:
        """Returns {module: str, reasoning: str, priority: int}"""
        pass
```

### 3. AI Agent Manager (`ai/ai_agent_manager.py`)

Manages agent lifecycle, context window, and history tracking.

### 4. Vulnerability Classifier (`ai/vulnerability_classifier.py`)

AI-assisted classification and severity scoring of findings.

### 5. False Positive Filter (`ai/false_positive_filter.py`)

Secondary AI pass to filter out likely false positives before they reach reports.

### 6. Automated Remediation (`ai/automated_remediation.py`)

Generates AI-synthesized fix suggestions for verified vulnerabilities.

## Supported AI Backends

### OpenAI
```yaml
# config.yaml
ai:
  provider: openai
  openai_api_key: "sk-..."
  openai_model: "gpt-4o"
```

### NVIDIA NIM
```yaml
ai:
  provider: nvidia
  nvidia_api_key: "nvapi-..."
  nvidia_model: "gemma-3"
```

### Ollama (Local)
```yaml
ai:
  provider: ollama
  ollama_base_url: "http://localhost:11434"
  ollama_model: "llama3"
```

## Prompt Engineering

The reasoning system uses structured prompts:

```
System: You are a security research agent. Available modules: {module_catalog}
Context: Target {target} has {ports} open, running {tech_stack}.
Findings so far: {findings}

Respond with JSON:
{
  "next_module": "module_name",
  "reasoning": "Why this module is next",
  "priority": 1-5
}
```

## Agent Tuning

### Reasoning Depth
```bash
# Shallow (fast, cheap) — 5 steps
darkwin hunt target.com --max-steps 5

# Deep (thorough, expensive) — 30 steps
darkwin hunt target.com --max-steps 30
```

### Module Filtering
```bash
# Restrict AI to specific vulnerability classes
darkwin hunt target.com --tags "sqli,xss,ssrf"
```

### Model Selection
Choose the model based on your needs:
- **GPT-4o**: Best reasoning, higher cost
- **Gemma-3 (NVIDIA NIM)**: Open-source, good for sensitive data
- **Llama 3 (Ollama)**: Fully local, no data leaves your network

## Context Management

The agent maintains a reasoning history that grows with each step. Long hunts may require context window management:
- **Short-term**: Last 5 reasoning steps + current findings
- **Long-term**: Summary of completed phases + top findings

## 5-Agent System

The dashboard visualizes 5 specialized agents:

| Agent | File | Function |
|---|---|---|
| **Strategist** | `core/agent_loop.py` | Tactical decision making |
| **Watchtower** | `core/mesh_manager.py` | Mesh node health monitoring |
| **Cartographer** | UI: `AttackSurfaceGraph.tsx` | 3D attack surface mapping |
| **Ghost** | `core/stealth.py` | Evasion & fingerprint randomization |
| **Sentinel** | `core/vuln_verifier.py` | Vulnerability verification |
