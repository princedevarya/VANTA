#!/usr/bin/env bash

set -e

PROJECT_NAME="VANTA"
FRONTEND_URL="http://localhost:5173"
BACKEND_URL="http://localhost:8000"
DOCS_URL="http://localhost:8000/docs"

echo ""
echo "============================================================"
echo "                         VANTA"
echo "          Virtual Attack & Network Testing Arena"
echo "============================================================"
echo ""
echo "  Starting VANTA..."
echo ""

docker compose up --build -d

echo ""
echo "  Waiting for VANTA backend..."
echo ""

until curl -fsS "${BACKEND_URL}/api/v1/health" >/dev/null 2>&1; do
    sleep 1
done

echo ""
echo "============================================================"
echo "                    VANTA IS READY"
echo "============================================================"
echo ""
echo "  Frontend    ->  ${FRONTEND_URL}"
echo "  API         ->  ${BACKEND_URL}"
echo "  API Docs    ->  ${DOCS_URL}"
echo ""
echo "  Open VANTA:"
echo "  ${FRONTEND_URL}"
echo ""
echo "  Stop VANTA:"
echo "  docker compose down"
echo ""
echo "============================================================"
echo ""
