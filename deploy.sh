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
    unzip

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Add ubuntu user to the docker group
usermod -aG docker ubuntu

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Install Nginx
apt-get install -y nginx

# Create app directory
mkdir -p /home/ubuntu/postbot
chown ubuntu:ubuntu /home/ubuntu/postbot

# Create basic Nginx configuration for your app
cat > /etc/nginx/sites-available/postbot << 'EOL'
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API - preserve /api prefix
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOL

# Enable the site configuration
ln -s /etc/nginx/sites-available/postbot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Restart Nginx to apply config
systemctl restart nginx

# Create environment variables file
cat > /home/ubuntu/postbot/.env << EOL
# Environment Variables
# These will be populated by the GitHub Actions workflow
SUPABASE_URL=__SUPABASE_URL__
GEMINI_API_KEY=__GEMINI_API_KEY__
REDDIT_CLIENT_ID=__REDDIT_CLIENT_ID__
REDDIT_CLIENT_SECRET=__REDDIT_CLIENT_SECRET__
REDDIT_USER_AGENT=__REDDIT_USER_AGENT__
SERPER_API_KEY=__SERPER_API_KEY__
SUPABASE_KEY=__SUPABASE_KEY__
SUPABASE_POSTGRES_DSN=__SUPABASE_POSTGRES_DSN__ 
VITE_SUPABASE_URL=__SUPABASE_URL__
VITE_SUPABASE_ANON_KEY=__SUPABASE_KEY__
API_URL=__API_URL__
REDIRECT_URL=__REDIRECT_URL__
VITE_API_URL=__VITE_API_URL__
VITE_REDIRECT_URL=__VITE_REDIRECT_URL__
# Add any other environment variables your application needs
EOL

# Create a script to pull and start the containers
cat > /home/ubuntu/deploy.sh << 'EOL'
#!/bin/bash

# Navigate to postbot directory
cd /home/ubuntu/postbot

# Create Docker config directory if it doesn't exist
mkdir -p /home/ubuntu/.docker

# Set up GitHub Container Registry authentication
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
fi

# Validate required environment variables
required_vars=(
  "API_URL"
  "REDIRECT_URL"
  "SUPABASE_URL"
  "SUPABASE_KEY"
  "GEMINI_API_KEY"
  "REDDIT_CLIENT_ID"
  "REDDIT_CLIENT_SECRET"
  "REDDIT_USER_AGENT"
  "SERPER_API_KEY"
  "VITE_SUPABASE_URL"
  "VITE_SUPABASE_ANON_KEY"
  "VITE_API_URL"
  "VITE_REDIRECT_URL"
)

for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo "Error: Required environment variable $var is not set"
    exit 1
  fi
done

# Pull latest images from GitHub Container Registry
echo "Pulling frontend image..."
docker pull ghcr.io/anukchat/postbot-frontend:latest
echo "Pulling backend image..."
docker pull ghcr.io/anukchat/postbot-backend:latest

# Copy the production docker-compose file from repository
cp ec2-docker-compose.yml /home/ubuntu/postbot/docker-compose.yml

# Start the containers with environment variables from .env file
echo "Starting containers..."
docker-compose up -d

# Check if containers are running
echo "Container status:"
docker ps
EOL

# Make the deploy script executable
chmod +x /home/ubuntu/deploy.sh
chown ubuntu:ubuntu /home/ubuntu/deploy.sh

# Set ownership for all created files
chown -R ubuntu:ubuntu /home/ubuntu/postbot

# Install certbot for SSL (Let's Encrypt)
apt-get install -y certbot python3-certbot-nginx

echo "System initialization complete. The GitHub Actions workflow will replace the placeholders in the .env file with actual secrets."