#!/bin/bash
set -e

# Deploy script for local Docker Compose + cloud readiness
# Usage:
#   chmod +x deploy-cloud.sh
#   ./deploy-cloud.sh

# Ensure env file exists
if [ ! -f .env ]; then
  echo ".env not found. Copy .env.example to .env and customize first."
  exit 1
fi

# Build the image
docker-compose build --no-cache

# Bring down existing containers and volumes for clean start
docker-compose down -v

# Bring up
docker-compose up -d

# Wait for startup logs
sleep 6

echo "--- web logs ---"
docker-compose logs --tail=30 web

echo "--- db logs ---"
docker-compose logs --tail=30 db || true

# Health check
echo "Checking health endpoint..."
if curl -sS http://localhost:5000/health | grep -q '{"status":"healthy"}'; then
  echo "App is healthy and accessible at http://localhost:5000/"
else
  echo "Health check failed. Inspect logs above."
  exit 2
fi

echo "Deployment script finished."
