#!/usr/bin/env bash

set -e

echo ""
echo "============================================================"
echo "                         VANTA"
echo "              Updating VANTA to latest version"
echo "============================================================"
echo ""

echo "  Checking repository status..."
echo ""

if [[ -n "$(git status --porcelain)" ]]; then
    echo "ERROR: You have local changes in the VANTA repository."
    echo ""
    echo "Please commit or stash your changes before updating."
    echo ""
    git status --short
    exit 1
fi

echo "  Pulling latest VANTA changes..."
echo ""

git pull --ff-only

echo ""
echo "  Rebuilding VANTA containers..."
echo ""

docker compose up --build -d

echo ""
echo "  Waiting for VANTA backend..."
echo ""

until docker compose exec -T backend python /app/healthcheck.py >/dev/null 2>&1; do
    sleep 2
done

echo ""
echo "============================================================"
echo "                    VANTA UPDATED"
echo "============================================================"
echo ""
echo "  Frontend    ->  http://localhost:5173"
echo "  API         ->  http://localhost:8000"
echo "  API Docs    ->  http://localhost:8000/docs"
echo ""
echo "  VANTA is running the latest version."
echo ""
echo "============================================================"
echo ""