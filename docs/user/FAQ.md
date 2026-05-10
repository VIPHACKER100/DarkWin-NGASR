# ❓ DARKWIN-NGASR: Frequently Asked Questions
## Developed by ARYAN AHIRWAR (VIPHACKER.100)

---

### 🚀 General Questions

#### What is DARKWIN-NGASR?
DARKWIN-NGASR is an autonomous security research platform that uses AI (LLMs) to automate the entire penetration testing lifecycle, from reconnaissance to reporting.

#### Is it free to use?
Yes, the core platform is open-source under the MIT license. However, you will need your own API keys for external services like OpenAI, Shodan, etc.

#### Who developed this?
The platform was developed by **ARYAN AHIRWAR (VIPHACKER.100)**.

---

### 🛠️ Setup & Technical

#### Does it work on Windows?
Yes! DARKWIN-NGASR is fully compatible with Windows 10/11. We recommend using PowerShell with our `setup.ps1` script or WSL2 for the best experience.

#### Why do I need Docker?
Docker is used to orchestrate the database (PostgreSQL), the caching layer (Redis), and the Next.js dashboard. It ensures a consistent environment for these critical services.

#### How do I fix "ModuleNotFoundError"?
This usually happens when you are not running the platform inside its virtual environment. Ensure you run `source .venv/bin/activate` (Linux/macOS) or `.\.venv\Scripts\Activate.ps1` (Windows) before running `darkwin`.

#### Can I use models other than OpenAI?
Yes! Through our NVIDIA NIM and Ollama integrations, you can use a wide variety of models. Check the [Advanced Usage Guide](ADVANCED.md) for more details.

---

### 🕵️ Security & Ethics

#### Is this a "Script Kiddie" tool?
No. DARKWIN-NGASR is designed for professional security researchers and bug bounty hunters. It provides deep visibility into its reasoning process and requires technical knowledge to configure and interpret results effectively.

#### Is it legal to use?
DARKWIN-NGASR is a tool. Like a hammer, it can be used for good or bad. You must **ALWAYS** obtain written permission before scanning any target that you do not own. Use it responsibly and legally.

#### Does it store my data?
All scan data is stored locally in your PostgreSQL/SQLite database. If you use external AI providers (like OpenAI), parts of your scan context (tech stack, port numbers) are sent to them for reasoning.

---

### 🤝 Support & Contribution

#### How can I report a bug?
Please open an issue on the GitHub repository or follow the steps in our [Security Policy](../../SECURITY.md) if it's a security-related bug.

#### How can I contribute a new module?
Check our [Module Development Guide](../dev/MODULES.md) for step-by-step instructions.

---
<div align="center">
<b>Autonomous · Distributed · Stealthy</b><br/>
© 2026 ARYAN AHIRWAR (VIPHACKER.100)
</div>
