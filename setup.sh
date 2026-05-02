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
readonly PROJECT_DIRS=(core modules pipelines ai automation integrations dashboards wordlists payloads logs reports)

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

# 2. Install Python Dependencies
info "Installing Python dependencies from requirements.txt..."
# Try standard install first
if pip install --user --upgrade -r requirements.txt; then
    success "Dependencies installed successfully"
elif pip install --user --upgrade --break-system-packages -r requirements.txt 2>/dev/null; then
    success "Dependencies installed successfully (using --break-system-packages)"
else
    error "Failed to install dependencies. Please try: pip install --user --upgrade typing-extensions>=4.11.0"
    exit 1
fi

# Install package in editable mode for development
if pip install -q -e .; then
    success "Package installed in editable mode"
else
    warn "Failed to install package in editable mode (non-fatal)"
fi

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
    if mkdir -p "$dir"; then
        touch "${dir}/.gitkeep"
        success "Directory ready: $dir"
    else
        error "Failed to create directory: $dir"
        exit 1
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
