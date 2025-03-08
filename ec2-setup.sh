#!/bin/bash

set -e

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo"
    exit 1
fi

# Update system and install required packages
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
    docker.io \
    docker-compose \
    nginx \
    unzip \
    curl \
    git

# Ensure Docker is running
sudo systemctl enable --now docker

# Add user to the docker group
sudo usermod -aG docker $USER
newgrp docker

# Set up project directory
sudo mkdir -p /home/ubuntu/postbot
sudo chown ubuntu:ubuntu /home/ubuntu/postbot

# Configure Nginx
sudo tee /etc/nginx/sites-available/postbot <<EOL
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api/ {
        proxy_pass http://localhost:8000/;
    }
}
EOL

sudo ln -sf /etc/nginx/sites-available/postbot /etc/nginx/sites-enabled/
sudo systemctl restart nginx

echo "EC2 setup complete!"
