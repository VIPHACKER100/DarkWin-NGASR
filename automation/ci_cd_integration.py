import os
import json

def generate_github_action():
    """
    Generates a GitHub Action workflow file for DARKWIN.
    """
    workflow = """
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
    return workflow
