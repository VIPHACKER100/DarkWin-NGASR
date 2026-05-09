#!/bin/bash
# DARKWIN Environment Repair Script
# Developed by ARYAN AHIRWAR (VIPHACKER.100)

echo "🛡️ Starting DARKWIN Environment Repair..."

# 1. Start Docker Services
echo "🚀 Starting Postgres and Redis via Docker..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d postgres redis
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    docker compose up -d postgres redis
else
    echo "❌ Docker not found or not running. Please start Docker Desktop/Service."
fi

# 2. Install Go Tools
echo "🛠️ Installing missing bug bounty tools..."
if command -v go &> /dev/null; then
    go install github.com/hahwul/dalfox/v2@latest
    go install github.com/lc/gau/v2/cmd/gau@latest
    go install github.com/tomnomnom/qsreplace@latest
    echo "✅ Go tools installation triggered."
else
    echo "❌ Go (golang) not found. Run 'sudo apt install golang' first."
fi

# 3. SQLite Check
if ! python3 -c "import sqlite3" &> /dev/null; then
    echo "❌ SQLite Python module missing."
    echo "👉 Run: sudo apt update && sudo apt install -y libsqlite3-dev"
else
    echo "✅ SQLite is healthy."
fi

echo "🏁 Repair script finished. Run 'darkwin doctor' again to verify."
