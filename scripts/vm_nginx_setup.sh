#!/usr/bin/env bash
set -euo pipefail

# Idempotent Nginx reverse-proxy setup for Postbot (modeled after origin/main).
# - Proxies /       -> http://localhost:<frontend-port>
# - Proxies /api/   -> http://localhost:<backend-port>/
# - Optionally provisions Let's Encrypt TLS via certbot.
#
# Usage:
#   sudo -n bash vm_nginx_setup.sh \
#     --domain example.com \
#     --frontend-port 3000 \
#     --backend-port 8000 \
#     --enable-ssl false
#
# For SSL:
#   sudo -n bash vm_nginx_setup.sh --domain example.com --enable-ssl true --email admin@example.com

DOMAIN=""
FRONTEND_PORT="3000"
BACKEND_PORT="8000"
ENABLE_SSL="false"
LETSENCRYPT_EMAIL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domain)
      DOMAIN="$2"; shift 2 ;;
    --frontend-port)
      FRONTEND_PORT="$2"; shift 2 ;;
    --backend-port)
      BACKEND_PORT="$2"; shift 2 ;;
    --enable-ssl)
      ENABLE_SSL="$2"; shift 2 ;;
    --email)
      LETSENCRYPT_EMAIL="$2"; shift 2 ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$DOMAIN" ]]; then
  echo "Usage: vm_nginx_setup.sh --domain <domain> [--enable-ssl true|false] [--email <addr>]" >&2
  exit 2
fi

if ! sudo -n true 2>/dev/null; then
  echo "ERROR: This setup requires non-interactive sudo (NOPASSWD) or root." >&2
  exit 1
fi

if ! command -v nginx >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    sudo -n apt-get update -y
    sudo -n apt-get install -y nginx
  elif command -v yum >/dev/null 2>&1; then
    sudo -n yum -y install nginx
  else
    echo "ERROR: Unsupported OS: need nginx installed." >&2
    exit 1
  fi
fi

if command -v systemctl >/dev/null 2>&1; then
  sudo -n systemctl enable nginx || true
  sudo -n systemctl start nginx || true
fi

# Debian/Ubuntu layout
SITES_AVAILABLE="/etc/nginx/sites-available"
SITES_ENABLED="/etc/nginx/sites-enabled"
CONF_PATH="$SITES_AVAILABLE/$DOMAIN"

sudo -n mkdir -p "$SITES_AVAILABLE" "$SITES_ENABLED"

# ACME webroot
sudo -n mkdir -p "/var/www/$DOMAIN/.well-known/acme-challenge"

if [[ "$ENABLE_SSL" == "true" ]]; then
  cat > /tmp/postbot_nginx_conf <<EOF
server {
    server_name $DOMAIN;
    client_max_body_size 10M;

    # ACME Challenge
    location ^~ /.well-known/acme-challenge/ {
        root /var/www/$DOMAIN;
        allow all;
    }

    # Proxy to Frontend (port $FRONTEND_PORT)
    location / {
        proxy_pass http://localhost:$FRONTEND_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_connect_timeout 90s;
        proxy_send_timeout 90s;
        proxy_read_timeout 120s;
    }

    # Proxy to Backend API (port $BACKEND_PORT)
    location /api/ {
        proxy_pass http://localhost:$BACKEND_PORT/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_connect_timeout 90s;
        proxy_send_timeout 90s;
        proxy_read_timeout 120s;
    }
}
EOF
else
  cat > /tmp/postbot_nginx_conf <<EOF
server {
    listen 80;
    server_name $DOMAIN;
    client_max_body_size 10M;

    location / {
        proxy_pass http://localhost:$FRONTEND_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 120s;
    }

    location /api/ {
        proxy_pass http://localhost:$BACKEND_PORT/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 120s;
    }
}
EOF
fi

sudo -n mv /tmp/postbot_nginx_conf "$CONF_PATH"

# Enable site
sudo -n ln -sf "$CONF_PATH" "$SITES_ENABLED/$DOMAIN"
# Disable default if present
sudo -n rm -f "$SITES_ENABLED/default" || true

sudo -n nginx -t
sudo -n systemctl reload nginx || sudo -n nginx -s reload

if [[ "$ENABLE_SSL" == "true" ]]; then
  if [[ -z "$LETSENCRYPT_EMAIL" ]]; then
    echo "ERROR: --email is required when --enable-ssl true" >&2
    exit 2
  fi

  echo "Setting up Let's Encrypt TLS via certbot..."
  if command -v apt-get >/dev/null 2>&1; then
    sudo -n apt-get update -y
    sudo -n apt-get install -y certbot python3-certbot-nginx
  elif command -v yum >/dev/null 2>&1; then
    sudo -n yum -y install certbot python3-certbot-nginx || sudo -n yum -y install certbot
  fi

  sudo -n certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$LETSENCRYPT_EMAIL" || {
    echo "Certbot failed. Ensure DNS points to this VM and ports 80/443 are open." >&2
    exit 1
  }

  sudo -n nginx -t
  sudo -n systemctl reload nginx || sudo -n nginx -s reload
fi

echo "Nginx setup complete for domain: $DOMAIN"
