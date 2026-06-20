# Security Policy
## Developed by ARYAN AHIRWAR (VIPHACKER.100)

At DARKWIN-NGASR, we take the security of our tools and the researchers who use them very seriously. This document outlines how to report vulnerabilities and our commitment to security.

---

## Supported Versions

We provide security updates for the following versions of DARKWIN-NGASR:

| Version | Supported |
| ------- | --------- |
| v2.0.x  | Yes |
| v1.2.x  | Limited |
| < v1.2  | No |

---

## Reporting a Vulnerability

If you discover a security vulnerability within DARKWIN-NGASR (e.g., in the core engine, dashboard, or modules), please do **NOT** open a public issue. Instead, follow these steps:

1. **Email**: Send a detailed report to **viphacker.100.org@gmail.com**.
2. **Details**: Include a description of the vulnerability, reproduction steps, and potential impact.
3. **PGP**: If possible, encrypt your email using our PGP key (available upon request).

We will acknowledge your report within **48 hours** and provide a timeline for a fix.

---

## Our Security Commitment

- **Fast Triage**: We prioritize security reports above all other features.
- **Transparent Communication**: We will keep you updated throughout the patching process.
- **Credit**: With your permission, we will credit you in our `CHANGELOG.md` and release notes.

---

## Codebase Security Practices

DARKWIN-NGASR follows these security best practices:

- **Exception Safety**: Zero bare `except:` or `except Exception` handlers — every exception is caught by specific type.
- **HTTP Client**: All HTTP requests use `httpx` with explicit timeouts and SSL verification.
- **Subprocess Safety**: Every external tool invocation uses `subprocess.run()` with explicit `check=True/False`.
- **Path Safety**: All file operations use `pathlib.Path` with explicit encoding and error handling.
- **Prompt Injection Prevention**: AI prompts are sanitized via `ai/security_utils.py` before reaching LLMs.
- **API Key Security**: API keys are passed via environment variables, never hardcoded or logged.
- **Scope Enforcement**: Target verification against authorized scope files before any scanning.
- **Legal Gate**: Mandatory legal acknowledgement before execution.

---

## Responsible Disclosure

We ask that you follow responsible disclosure guidelines:
- Give us reasonable time to investigate and fix the issue before making any information public.
- Do not exploit the vulnerability beyond what is necessary for a Proof of Concept (PoC).
- Do not use the vulnerability to access user data or disrupt services.

---

<div align="center">
<b>Securing the Future of Autonomous Research</b><br/>
(C) 2026 ARYAN AHIRWAR (VIPHACKER.100)
</div>
