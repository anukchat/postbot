#!/bin/bash

# This script helps to manually authenticate with GitHub Container Registry
# Usage: ./manual_ghcr_auth.sh <github_username> <github_token>

if [ $# -ne 2 ]; then
    echo "Usage: $0 <github_username> <github_token>"
    echo "Example: $0 anukchat ghp_abcdef123456"
    exit 1
fi

GITHUB_USERNAME="$1"
GITHUB_TOKEN="$2"

# Create Docker config directory if it doesn't exist
mkdir -p ~/.docker

# Set up GitHub Container Registry authentication
echo "Setting up GitHub Container Registry authentication..."
echo '{
  "auths": {
    "ghcr.io": {
      "auth": "'$(echo -n "$GITHUB_USERNAME:$GITHUB_TOKEN" | base64)'"
    }
  }
}' > ~/.docker/config.json

# Ensure proper permissions
chmod 600 ~/.docker/config.json

echo "Authentication config created at ~/.docker/config.json"
echo "Testing authentication..."

# Try docker login to verify credentials
echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_USERNAME" --password-stdin

if [ $? -eq 0 ]; then
    echo "Authentication successful! You can now pull images from ghcr.io"
    
    # Pull the images
    echo "Pulling frontend image..."
    docker pull ghcr.io/anukchat/postbot-frontend:latest
    
    echo "Pulling backend image..."
    docker pull ghcr.io/anukchat/postbot-backend:latest
    
    echo "Starting containers with docker-compose..."
    cd /home/ubuntu/postbot
    docker-compose up -d
    
    echo "Container status:"
    docker ps
else
    echo "Authentication failed. Please check your GitHub username and token."
fi