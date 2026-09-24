#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Starting services with docker compose..."
docker compose up -d

echo ""
echo "Services started:"
echo "  - Backend:  http://localhost:8000"
echo "  - Frontend: http://localhost:7888"
echo ""
echo "To view logs: docker compose logs -f"
echo "To stop:      docker compose down"
