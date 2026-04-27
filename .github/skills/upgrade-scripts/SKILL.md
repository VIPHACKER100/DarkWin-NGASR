---
name: upgrade-scripts
description: "Use when: modernizing Python or shell scripts with code best practices, security hardening, dependency updates, or compatibility improvements. Guides systematic review, refactoring, security patching, and testing."
---

# Script Upgrade Workflow

Systematically modernize and harden Python and shell scripts across the codebase. This skill provides a checkpoint-driven process for code modernization, security hardening, and best-practice implementation.

## When to Use This Skill

- Upgrading Python scripts to modern standards (3.10+)
- Modernizing shell scripts with best practices
- Adding security hardening to existing scripts
- Implementing dependency updates safely
- Bulk refactoring for consistency across the codebase

## Workflow Overview

| Phase | Objective | Scope |
|-------|-----------|-------|
| **1. Discovery** | Audit existing scripts | Identify candidates, versions, patterns |
| **2. Assessment** | Evaluate upgrade paths | Risk, dependencies, compatibility |
| **3. Planning** | Define upgrade strategy | Per-script targets & checklist |
| **4. Execution** | Implement changes | Modernization, hardening, refactoring |
| **5. Validation** | Verify functionality | Testing, linting, security scan |
| **6. Documentation** | Update records | Changelog, comments, assumptions |

---

## Phase 1: Discovery

### List All Scripts
Identify all Python and shell scripts that need review:

```powershell
# Python scripts
Get-ChildItem -Recurse -Filter "*.py" | Select-Object FullName

# Shell scripts
Get-ChildItem -Recurse -Filter "*.sh" | Select-Object FullName
```

### Collect Baseline Metrics
For each script, record:
- **File path** and size
- **Current Python version** (if applicable) or shell type
- **Key dependencies** imported
- **Last modified date**
- **Usage context** (entry point, module, test, automation)

---

## Phase 2: Assessment

### Python Scripts: Version & Compatibility Check

**Questions to answer:**
- [ ] Is script using Python 2? (Deprecated—migrate to 3.10+)
- [ ] Are dependencies pinned? Check `requirements.txt`, `pyproject.toml`, imports
- [ ] Are there deprecated library calls? (e.g., `imp`, `collections.MutableMapping`)
- [ ] Does script use async/await appropriately?
- [ ] Is error handling explicit (try/except specificity)?

**Common Python Upgrade Targets:**
- Type hints on function signatures
- `pathlib.Path` instead of `os.path`
- f-strings instead of `.format()` or `%` formatting
- Context managers (`with` statements) for file handling
- Explicit exception handling (avoid bare `except:`)

### Shell Scripts: Best Practices Check

**Questions to answer:**
- [ ] Does script use `set -e` and `set -u` for safety?
- [ ] Are variables quoted (avoid word splitting)?
- [ ] Does script validate inputs and exit codes?
- [ ] Are heredocs used safely (avoid `$` expansion if not needed)?
- [ ] Is script compatible with `bash` 4.0+?

**Common Shell Script Upgrade Targets:**
- Add shebang validation: `#!/bin/bash` with strict modes
- Replace backticks with `$(...)` syntax
- Validate all external command return codes
- Use local variables in functions
- Document assumptions (OS, prerequisites)

### Security Hardening Assessment

**For both Python & Shell:**
- [ ] No hardcoded secrets or credentials
- [ ] Input validation on CLI args and environment variables
- [ ] Proper file permissions (scripts should be 0755)
- [ ] No insecure random/hash functions (`random.randint`, `md5`)
- [ ] Use secure defaults (fail closed, deny by default)

---

## Phase 3: Planning

### Create Upgrade Checklist Per Script

**Template:**
```yaml
Script: path/to/script.py
Current Version: Python 3.8
Target Version: Python 3.11
Risk Level: [Low / Medium / High]

Upgrade Tasks:
  [ ] Add type hints to all functions
  [ ] Replace deprecated imports
  [ ] Update dependency versions
  [ ] Refactor error handling
  [ ] Add security validation
  [ ] Update comments & docstrings
  [ ] Run linting & tests
  [ ] Update CHANGELOG

Blockers:
  - (none, or list if any)

Dependencies to Update:
  - (list libraries with versions)
```

### Prioritize Upgrades
1. **Critical scripts** (high usage, security-sensitive)
2. **Entry points** (main application scripts)
3. **Utilities** (helpers, supporting code)
4. **Tests** (minimal risk, good for practice)

---

## Phase 4: Execution

### Python Script Modernization

**Step 1: Add Type Hints**
```python
# Before
def process_file(path, output):
    with open(path) as f:
        data = f.read()
    return data.upper()

# After
from pathlib import Path
from typing import Union

def process_file(path: Union[str, Path], output: Path) -> str:
    with open(Path(path)) as f:
        data = f.read()
    return data.upper()
```

**Step 2: Use Modern Syntax**
```python
# Before
message = "Hello, {}".format(name)
paths = [os.path.join(root, f) for f in os.listdir(root)]

# After
message = f"Hello, {name}"
paths = [p for p in Path(root).iterdir()]
```

**Step 3: Hardened Error Handling**
```python
# Before
try:
    result = risky_operation()
except:
    pass

# After
try:
    result = risky_operation()
except ValueError as e:
    logging.error(f"Invalid input: {e}")
    raise
except Exception as e:
    logging.critical(f"Unexpected error: {e}")
    raise
```

**Step 4: Security Hardening**
```python
# Before
import random
secret = random.randint(0, 1000000)

# After
import secrets
secret = secrets.randbits(32)

# Before
import hashlib
hash_val = hashlib.md5(data).hexdigest()

# After
import hashlib
hash_val = hashlib.sha256(data).hexdigest()

# Before
user_input = input("Enter command: ")
os.system(user_input)

# After
import shlex
user_input = input("Enter command: ")
args = shlex.split(user_input)
subprocess.run(args, check=True)  # Never shell=True with user input
```

### Shell Script Modernization

**Step 1: Add Safety Flags**
```bash
# Before
#!/bin/bash
# ... script content

# After
#!/bin/bash
set -euo pipefail
IFS=$'\n\t'
# ... script content
```

**Step 2: Quote Variables & Use Modern Syntax**
```bash
# Before
file=$1
cat $file | grep "pattern"

# After
file="$1"
grep "pattern" < "$file"
# or
grep "pattern" "$file"
```

**Step 3: Validate Inputs**
```bash
# Before
script_name=$1
rm -rf "$script_name"

# After
script_name="$1"
if [[ -z "$script_name" ]]; then
    echo "Error: Script name required" >&2
    exit 1
fi
if [[ ! -d "$script_name" ]]; then
    echo "Error: Directory not found" >&2
    exit 1
fi
rm -rf "$script_name"
```

**Step 4: Document & Validate**
```bash
#!/bin/bash
# Script: cleanup.sh
# Purpose: Remove temporary files
# Usage: ./cleanup.sh [directory]
# Requires: bash 4.0+

set -euo pipefail

readonly DIR="${1:-.}"
readonly MAX_AGE_DAYS=30

[[ -d "$DIR" ]] || { echo "Error: Invalid directory"; exit 1; }

find "$DIR" -type f -mtime "+$MAX_AGE_DAYS" -delete
```

---

## Phase 5: Validation

### Code Quality Checks

**Python:**
```powershell
# Linting
python -m pylint script.py
python -m flake8 script.py

# Type checking
mypy script.py

# Security scan
bandit script.py

# Tests (if applicable)
pytest tests/ -v
```

**Shell:**
```powershell
# Linting
shellcheck script.sh

# Test execution
bash script.sh --help
bash script.sh [test-args]
```

### Functional Testing

For each upgraded script:
1. Run script with typical inputs → verify output matches expected
2. Test edge cases (empty input, special chars, very large files)
3. Test error paths (missing files, permission denied, invalid args)
4. Verify exit codes are correct (0 success, non-zero failure)

### Security Validation

- [ ] No hardcoded secrets in upgraded code
- [ ] Input validation passes malicious input tests
- [ ] Dependency versions are current (no known CVEs)
- [ ] File permissions are secure (scripts 0755, configs 0640)
- [ ] No use of insecure crypto or RNG functions

---

## Phase 6: Documentation

### Update Script Comments

```python
"""
Script: analyze_findings.py
Purpose: Parse vulnerability findings and generate summary report
Version: 2.0 (Python 3.11+)
Last Updated: 2026-04-27

Dependencies:
  - pydantic>=2.0
  - requests>=2.31

Author: Security Team
License: See LICENSE file
"""
```

### Update CHANGELOG.md

```markdown
## [Version X.Y.Z] - 2026-04-27

### Changed
- **Upgraded script_name.py**: Added type hints, modernized to Python 3.11
- **Upgraded setup.sh**: Added safety flags (set -euo pipefail), improved validation
- Replaced deprecated function calls across codebase

### Security
- Replaced md5 hashing with SHA-256 in crypto operations
- Added input validation to all CLI entry points
- Fixed shell injection vulnerability in command builder

### Removed
- Python 2 compatibility code
- Deprecated library calls (imp, collections.MutableMapping)
```

### Document Known Limitations

If upgrade introduces constraints, document them:
```python
# NOTE: Now requires Python 3.10+ for walrus operator usage
# See: https://docs.python.org/3/whatsnew/3.10.html
```

---

## Checklist: Ready to Ship

Before marking scripts as upgraded:

- [ ] All type hints added and validated (`mypy` passes)
- [ ] All linting issues resolved (`pylint`, `flake8`, `shellcheck`)
- [ ] All tests pass (unit, integration, security)
- [ ] Security scan clean (no CVEs, no secrets, no insecure patterns)
- [ ] Comments and docstrings updated
- [ ] CHANGELOG entry added
- [ ] Code review approved
- [ ] Backward compatibility verified (if applicable)
- [ ] Performance regression tested (no slowdown)

---

## Example Prompts to Invoke This Skill

> "Upgrade all Python scripts to modern best practices and add type hints"

> "Harden shell scripts with security checks and error handling"

> "Modernize setup.sh and requirements.txt for Python 3.11+"

> "Run full upgrade workflow on /modules/vulnerability_engine/"

> "Create upgrade plan for all entry-point scripts"

---

## Related Skills / Customizations

- **Code Review Instructions**: Create a `.github/instructions/code-review.instructions.md` to enforce code quality gates
- **Security Hardening**: Create skill for OWASP compliance, API security, or cryptography best practices
- **Testing Workflow**: Create skill for test-driven upgrade strategy
- **Performance Profiling**: Create skill for measuring performance impact of modernization changes

---

## References

- [Python 3.11 Migration Guide](https://docs.python.org/3/whatsnew/3.11.html)
- [Bash Best Practices](https://mywiki.wooledge.org/BashGuide/Practices)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [Type Hints in Python](https://docs.python.org/3/library/typing.html)
- [ShellCheck](https://www.shellcheck.net/)
