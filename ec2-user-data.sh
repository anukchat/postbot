#!/bin/bash

# Log all output
exec > >(tee /var/log/user-data.log) 2>&1
echo "Starting EC2 initialization script..."

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

echo "Installing Docker..."
# Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Add ubuntu user to the docker group
usermod -aG docker ubuntu

# Create app directory
mkdir -p /home/ubuntu/postbot
chown ubuntu:ubuntu /home/ubuntu/postbot

echo "Configuring Nginx..."
# Create basic Nginx configuration
cat > /etc/nginx/sites-available/postbot << 'EOL'
server {
    listen 80;
    server_name _;
    
    client_max_body_size 10M;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 120s;
    }

    location /api {
        rewrite ^/api(/.*)$ $1 break;
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 120s;
    }
}
EOL

# Enable the site configuration
ln -sf /etc/nginx/sites-available/postbot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Restart Nginx to apply config
systemctl restart nginx

echo "Creating deployment script..."
# Create a deployment script
cat > /home/ubuntu/deploy.sh << 'EOL'
#!/bin/bash

# Log all output to a file
exec > >(tee -a /home/ubuntu/deployment.log) 2>&1
echo "Starting deployment at $(date)"

# Navigate to postbot directory
cd /home/ubuntu/postbot

# Ensure Docker config directory exists
mkdir -p /home/ubuntu/.docker

# Set up GitHub Container Registry auth
if [ -n "$GITHUB_TOKEN" ]; then
  echo "Setting up GitHub Container Registry authentication..."
  echo '{
    "auths": {
      "ghcr.io": {
        "auth": "'$(echo -n "$GITHUB_USERNAME:$GITHUB_TOKEN" | base64)'"
      }
    }
  }' > /home/ubuntu/.docker/config.json
  chmod 600 /home/ubuntu/.docker/config.json
  
  # Also try direct login
  echo "Logging in to GitHub Container Registry..."
  echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_USERNAME" --password-stdin
fi

echo "Stopping existing containers..."
# Stop and remove existing containers if they exist
docker stop postbot-frontend postbot-backend 2>/dev/null || echo "No containers to stop"
docker rm postbot-frontend postbot-backend 2>/dev/null || echo "No containers to remove"

echo "Pulling latest images..."
# Pull latest images with verbose error handling
docker pull ghcr.io/anukchat/postbot-frontend:latest
if [ $? -ne 0 ]; then
  echo "ERROR: Failed to pull frontend image"
  echo "Debugging information:"
  docker info
  cat /home/ubuntu/.docker/config.json || echo "No config file found"
  exit 1
fi

docker pull ghcr.io/anukchat/postbot-backend:latest
if [ $? -ne 0 ]; then
  echo "ERROR: Failed to pull backend image"
  exit 1
fi

echo "Starting containers..."
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
echo "Running containers:"
docker ps

echo "Deployment completed at $(date)"
EOL

# Make the deploy script executable
chmod +x /home/ubuntu/deploy.sh
chown ubuntu:ubuntu /home/ubuntu/deploy.sh

# Create empty .env file
touch /home/ubuntu/postbot/.env
chown ubuntu:ubuntu /home/ubuntu/postbot/.env

echo "System initialization complete at $(date)"
echo "The GitHub Actions workflow will populate the .env file with actual secrets."