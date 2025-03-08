#!/bin/bash

# Update the system
apt-get update
apt-get upgrade -y

# Install required packages
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    nginx

# Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Add ubuntu user to the docker group
usermod -aG docker ubuntu

# Create app directory
mkdir -p /home/ubuntu/postbot
chown ubuntu:ubuntu /home/ubuntu/postbot

# Create basic Nginx configuration
cat > /etc/nginx/sites-available/postbot << 'EOL'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        rewrite ^/api(/.*)$ $1 break;
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOL

# Enable the site configuration
ln -s /etc/nginx/sites-available/postbot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Restart Nginx to apply config
systemctl restart nginx

# Create a deployment script
cat > /home/ubuntu/deploy.sh << 'EOL'
#!/bin/bash

# Navigate to postbot directory
cd /home/ubuntu/postbot

# Ensure Docker config directory exists
mkdir -p /home/ubuntu/.docker

# Set up GitHub Container Registry auth
if [ -n "$GITHUB_TOKEN" ]; then
  echo '{
    "auths": {
      "ghcr.io": {
        "auth": "'$(echo -n "$GITHUB_USERNAME:$GITHUB_TOKEN" | base64)'"
      }
    }
  }' > /home/ubuntu/.docker/config.json
  chmod 600 /home/ubuntu/.docker/config.json
fi

# Stop and remove existing containers if they exist
docker stop postbot-frontend postbot-backend || true
docker rm postbot-frontend postbot-backend || true

# Pull latest images
docker pull ghcr.io/anukchat/postbot-frontend:latest
docker pull ghcr.io/anukchat/postbot-backend:latest

# Start containers
docker run -d \
  --name postbot-frontend \
  --env-file .env \
  -p 3000:3000 \
  --restart always \
  ghcr.io/anukchat/postbot-frontend:latest

docker run -d \
  --name postbot-backend \
  --env-file .env \
  -p 8000:8000 \
  --restart always \
  ghcr.io/anukchat/postbot-backend:latest

# Show running containers
docker ps
EOL

# Make the deploy script executable
chmod +x /home/ubuntu/deploy.sh
chown ubuntu:ubuntu /home/ubuntu/deploy.sh

# Create empty .env file
touch /home/ubuntu/postbot/.env
chown ubuntu:ubuntu /home/ubuntu/postbot/.env

# Force merge deployment_check into main
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
git checkout main
git merge deployment_check --strategy-option theirs
git push origin main --force

echo "System initialization complete. The GitHub Actions workflow will populate the .env file with actual secrets."
