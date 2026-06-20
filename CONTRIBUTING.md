# Contributing to DARKWIN-NGASR
## Developed by ARYAN AHIRWAR (VIPHACKER.100)

First off, thank you for considering contributing to DARKWIN-NGASR! It's people like you that make DARKWIN such a powerful tool for the security community.

---

## Table of Contents
1. [Code of Conduct](#code-of-conduct)
2. [How Can I Contribute?](#how-can-i-contribute)
3. [Style Guidelines](#style-guidelines)
4. [Pull Request Process](#pull-request-process)

---

## Code of Conduct
This project and everyone participating in it is governed by the [Project Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

## How Can I Contribute?

### Reporting Bugs
- Use the **GitHub Issue Tracker**.
- Describe the bug in detail and provide reproduction steps.
- Include your environment details (OS, Python version).

### Suggesting Enhancements
- Open an issue with the tag `enhancement`.
- Explain why the feature would be useful and how it should work.

### Developing Modules
- Create a new module in the appropriate sub-directory of `modules/`.
- Ensure it follows the [Module Development Guide](docs/dev/MODULES.md).
- Write a unit test for your module in `tests/`.

---

## Style Guidelines

### Python Style
- Follow **PEP 8**.
- Use **Type Hints** for all function signatures (`def func() -> None:`).
- Use **Async/Await** for I/O bound operations.
- Write descriptive docstrings for all classes and functions (PEP 257 style with `Args:`, `Returns:`, `Raises:` sections).

### Exception Handling
- **NEVER** use bare `except:` or `except Exception:`.
- Always catch specific exception types: `httpx.RequestError`, `OSError`, `ValueError`, `json.JSONDecodeError`, `subprocess.CalledProcessError`, etc.
- Use multiple `except` clauses for different error types when appropriate.

### File Operations
- Use `pathlib.Path` instead of `os.path.*`.
- Always use context managers (`with` statements) for file operations.
- Specify `encoding="utf-8"` on text file operations.
- Use `.unlink(missing_ok=True)` instead of `os.remove()`.

### HTTP Client
- Use `httpx` instead of `requests`.
- Always specify timeouts on HTTP calls.
- Handle `httpx.RequestError` and `httpx.HTTPStatusError` explicitly.

### Subprocess
- Always specify `check=True` or `check=False` on `subprocess.run()` calls.
- Handle `subprocess.CalledProcessError`, `subprocess.TimeoutExpired`, and `FileNotFoundError` as appropriate.

### Commit Messages
- Use the imperative mood ("Add feature" instead of "Added feature").
- Keep the first line under 50 characters.
- Reference issues and pull requests after the first line.

---

## Pull Request Process

1. **Fork the Repo**: Create your own copy of the repository.
2. **Create a Branch**: `git checkout -b feature/amazing-module`.
3. **Write Code**: Ensure your changes follow the style guidelines above.
4. **Run Tests**: `pytest tests/ -v` must pass.
5. **Verify Compilation**: `python -m py_compile` on all new/modified files.
6. **Submit PR**: Provide a clear description of the changes in your PR.

---

<div align="center">
<b>Build the Future of Autonomous Security</b><br/>
(C) 2026 ARYAN AHIRWAR (VIPHACKER.100)
</div>
