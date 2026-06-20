"""DARKWIN CI/CD Integration module.

Generates GitHub Action workflow files for automated DARKWIN scanning in CI pipelines.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

def generate_github_action() -> str:
    """Generate a GitHub Action workflow YAML for DARKWIN scanning.

    Returns:
        Workflow YAML string.
    """
    return """
name: DARKWIN Security Scan
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -e .
    - name: Run Recon
      run: darkwin recon example.com --scope-file scope.json
"""
