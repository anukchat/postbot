#!/bin/bash

# This script updates your EC2 instance to fix the API connection issues
# Usage: ./update-ec2-deployment.sh <ec2_host> <ssh_key_path>

if [ $# -ne 2 ]; then
    echo "Usage: $0 <ec2_host> <ssh_key_path>"
    echo "Example: $0 15.207.19.241 ~/.ssh/ec2-key.pem"
    exit 1
fi

EC2_HOST="$1"
SSH_KEY="$2"

echo "Updating EC2 instance at $EC2_HOST..."

# Copy the updated docker-compose.yml to the EC2 instance
scp -i "$SSH_KEY" ec2-docker-compose.yml ubuntu@"$EC2_HOST":/home/ubuntu/postbot/docker-compose.yml

# Connect to the EC2 instance and restart the containers
ssh -i "$SSH_KEY" ubuntu@"$EC2_HOST" << 'EOF'
cd /home/ubuntu/postbot

# Stop the current containers
docker-compose down

# Pull the latest images (optional, remove if you want to use the existing images)
docker pull ghcr.io/anukchat/postbot-frontend:latest
docker pull ghcr.io/anukchat/postbot-backend:latest

# Start the containers with the new configuration
docker-compose up -d

# Check container status
docker ps

# Check logs for potential issues
echo "Frontend logs:"
docker logs postbot-frontend --tail 10

echo "Backend logs:"
docker logs postbot-backend --tail 10

# Check Nginx configuration
sudo nginx -t
EOF

echo "Update complete! Your web application should now be accessible at http://$EC2_HOST"
echo "If you're still experiencing issues, check the logs on your EC2 instance:"
echo "ssh -i \"$SSH_KEY\" ubuntu@\"$EC2_HOST\" \"docker logs postbot-frontend\""