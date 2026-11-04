#!/usr/bin/env bash
set -e

echo "================================================="
echo "       SprintLens - Local Environment Setup      "
echo "================================================="

if [ ! -f ".env" ]; then
    echo "[+] Creating .env from .env.example..."
    cp .env.example .env
else
    echo "[i] .env file already exists."
fi

echo ""
echo "[+] Checking prerequisites..."

command -v node >/dev/null 2>&1 && echo "  - Node.js: $(node -v)" || echo "  - Node.js: NOT FOUND"
command -v pnpm >/dev/null 2>&1 && echo "  - pnpm: $(pnpm -v)" || echo "  - pnpm: NOT FOUND"
command -v python3 >/dev/null 2>&1 && echo "  - Python: $(python3 --version)" || echo "  - Python: NOT FOUND"
command -v docker >/dev/null 2>&1 && echo "  - Docker: $(docker --version)" || echo "  - Docker: NOT FOUND"

echo ""
echo "[+] Setup check complete!"
echo "To start PostgreSQL: docker-compose up -d postgres"
