#!/usr/bin/env bash
# DARKWIN — Tool & Environment Setup Script
# Developed by ARYAN AHIRWAR (VIPHACKER.100)

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; }

check_tool() {
    if command -v "$1" >/dev/null 2>&1; then
        success "$1 is installed"
    else
        warn "$1 is NOT installed. Please install it manually."
    fi
}

info "Starting DARKWIN setup..."

# 1. Check Python Version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
if [[ $(echo -e "3.11\n$PYTHON_VERSION" | sort -V | head -n1) == "3.11" ]]; then
    success "Python $PYTHON_VERSION detected"
else
    error "Python 3.11+ is required. Detected: $PYTHON_VERSION"
    exit 1
fi

# 2. Install Python dependencies
info "Installing Python dependencies..."
pip install -r requirements.txt
pip install -e .

# 3. Check for external tools
info "Checking for external security tools..."
TOOLS=(nmap subfinder httpx nuclei ffuf amass katana sqlmap dalfox masscan)
for tool in "${TOOLS[@]}"; do
    check_tool "$tool"
done

# 4. Create directory structure
info "Ensuring directory structure exists..."
DIRS=(core modules pipelines ai automation integrations dashboards wordlists payloads logs reports)
for dir in "${DIRS[@]}"; do
    mkdir -p "$dir"
    touch "$dir/.gitkeep"
done

# 5. Check for Legal Acknowledgement
if [ ! -f .acknowledged ]; then
    warn "LEGAL.md has not been acknowledged yet."
fi

success "DARKWIN setup completed successfully!"
info "Next steps:"
info "1. Acknowledge LEGAL.md by running 'darkwin' for the first time."
info "2. Configure config.yaml."
info "3. Initialize database with 'python core/migrations/init_db.py'."
