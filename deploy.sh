#!/bin/bash

set -e  # Exit if any command fails

echo "Pulling latest images..."
docker pull ghcr.io/anukchat/postbot-frontend:latest
docker pull ghcr.io/anukchat/postbot-backend:latest

echo "Stopping existing containers..."
docker-compose down

echo "Starting new containers..."
docker-compose up -d --remove-orphans

echo "Deployment complete!"
docker ps
