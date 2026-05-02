#!/usr/bin/env bash
# ============================================================================
# DARKWIN — Environment & Tool Setup Script
# ============================================================================
# Purpose: Initialize DARKWIN environment with Python, dependencies, and
#          external security tools.
# Author: ARYAN AHIRWAR (VIPHACKER.100)
# License: See LICENSE file
# Usage: ./setup.sh
# ============================================================================

# Strict mode: exit on error (-e), undefined vars (-u), pipe failures (-o pipefail)
set -euo pipefail

# Color definitions for terminal output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'  # No Color

# Minimum required Python version
readonly MIN_PYTHON_VERSION="3.11"

# External security tools required
readonly SECURITY_TOOLS=(nmap subfinder httpx nuclei ffuf amass katana sqlmap dalfox masscan)

# Project directories
PROJECT_DIRS=(core modules pipelines ai automation integrations dashboards wordlists payloads logs reports)

# ============================================================================
# Output Functions
# ============================================================================

info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; }

# ============================================================================
# Tool Verification
# ============================================================================

check_tool() {
    # Check if a command-line tool is installed and available in PATH.
    if command -v "$1" > /dev/null 2>&1; then
        success "$1 is installed"
    else
        warn "$1 is NOT installed. Please install it manually."
    fi
}

# ============================================================================
# Setup Execution
# ============================================================================

info "Starting DARKWIN setup..."
info ""

# 1. Check Python Version
info "Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)

if [[ "$(printf '%s\n' "$MIN_PYTHON_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" == "$MIN_PYTHON_VERSION" ]]; then
    success "Python $PYTHON_VERSION detected"
else
    error "Python $MIN_PYTHON_VERSION+ is required. Detected: $PYTHON_VERSION"
    exit 1
fi

info ""

# 2. Setup Virtual Environment
VENV_DIR=".venv"
info "Setting up virtual environment at ${VENV_DIR}..."
if [ ! -d "${VENV_DIR}" ]; then
    python3 -m venv "${VENV_DIR}"
    success "Virtual environment created"
else
    success "Virtual environment already exists"
fi

# Activate the venv for this script session
source "${VENV_DIR}/bin/activate"
success "Virtual environment activated"

# 3. Install Python Dependencies inside venv (isolated from system)
info "Installing Python dependencies inside venv..."
pip install --upgrade pip setuptools wheel
pip install --upgrade "typing-extensions>=4.11.0" "pydantic-core>=2.18.0"

if pip install -r requirements.txt; then
    success "Dependencies installed successfully"
else
    error "Failed to install dependencies."
    exit 1
fi

# Ensure __init__.py files exist
info "Ensuring package structure..."
find . -type d \( -name "core" -o -name "modules" -o -name "pipelines" -o -name "ai" -o -name "automation" -o -name "integrations" -o -name "dashboards" \) -exec touch {}/__init__.py \;

# Install package in editable mode
if pip install -e .; then
    success "Package installed in editable mode"
else
    warn "Failed to install package in editable mode (non-fatal)"
fi

info ""
info "⚡ IMPORTANT: To use DARKWIN, activate the venv first:"
info "   source .venv/bin/activate"
info "   darkwin --help"

info ""

# 3. Check External Security Tools & Environment
info "Checking for external security tools and environment..."
ENVIRONMENT_TOOLS=(docker node npm)
for tool in "${SECURITY_TOOLS[@]}" "${ENVIRONMENT_TOOLS[@]}"; do
    check_tool "$tool"
done

info ""

# 4. Create Directory Structure
info "Creating/validating project directory structure..."
PROJECT_DIRS+=(dashboards/frontend-next/public/reports)
for dir in "${PROJECT_DIRS[@]}"; do
    if mkdir -p "$dir" 2>/dev/null; then
        # Use || true to prevent script exit on touch permission errors
        touch "${dir}/.gitkeep" 2>/dev/null || true
        success "Directory ready: $dir"
    else
        # If mkdir fails but directory exists, we might still be okay
        if [ -d "$dir" ]; then
            success "Directory already exists: $dir"
        else
            error "Failed to create directory: $dir"
            exit 1
        fi
    fi
done

info ""

# 5. Check Legal Acknowledgement Status
info "Checking legal acknowledgement status..."
if [ -f .acknowledged ]; then
    success "Legal terms have been acknowledged"
else
    warn "Legal terms have NOT been acknowledged yet"
    warn "Run 'darkwin' or 'python core/darkwin.py' to complete acknowledgement"
fi

info ""

# 6. Display Next Steps
success "DARKWIN-NGASR Zenith Setup completed successfully!"
info ""
info "Next steps:"
info "  1. Complete legal acknowledgement: python core/darkwin.py"
info "  2. Run automated diagnostics: python core/darkwin.py doctor --fix"
info "  3. Launch full ecosystem (Recommended): docker-compose up -d --build"
info "  4. Start a manual hunt: python core/darkwin.py hunt example.com"
info ""
info "For more information, see: README.md"
info ""
