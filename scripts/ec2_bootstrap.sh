#!/usr/bin/env bash
set -euo pipefail

# One-time EC2/VM setup for Postbot:
# - Install Docker Engine + docker compose plugin (Ubuntu/Debian)
# - Optionally install and configure Nginx using a user-provided template
#
# Usage examples:
#   sudo -n bash scripts/ec2_bootstrap.sh --install-docker
#   sudo -n bash scripts/ec2_bootstrap.sh --install-docker --setup-nginx \
#     --domain example.com \
#     --nginx-template scripts/nginx/postbot.conf.template \
#     --frontend-port 3000 --backend-port 8000

INSTALL_DOCKER="false"
SETUP_NGINX="false"
DOMAIN=""
NGINX_TEMPLATE=""
FRONTEND_PORT="3000"
BACKEND_PORT="8000"
ENABLE_SSL="false"
LETSENCRYPT_EMAIL=""
SUDO=""

usage() {
  cat <<'EOF'
Usage: sudo -n bash scripts/ec2_bootstrap.sh [options]

Options:
  --install-docker              Install Docker Engine + docker compose plugin (Ubuntu/Debian)
  --setup-nginx                 Install and configure Nginx
  --domain <domain>             Domain name for server_name (required when --setup-nginx)
  --nginx-template <path>       Path to nginx template file (required when --setup-nginx)
  --frontend-port <port>        Frontend port to proxy to (default: 3000)
  --backend-port <port>         Backend port to proxy to (default: 8000)
  --enable-ssl <true|false>     If true, try to provision Let's Encrypt via certbot (default: false)
  --email <email>               Email for Let's Encrypt (required when --enable-ssl true)

Notes:
- This script targets Ubuntu/Debian via apt.
- Run it on the server (via ssh) with sudo.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install-docker)
      INSTALL_DOCKER="true"; shift ;;
    --setup-nginx)
      SETUP_NGINX="true"; shift ;;
    --domain)
      DOMAIN="$2"; shift 2 ;;
    --nginx-template)
      NGINX_TEMPLATE="$2"; shift 2 ;;
    --frontend-port)
      FRONTEND_PORT="$2"; shift 2 ;;
    --backend-port)
      BACKEND_PORT="$2"; shift 2 ;;
    --enable-ssl)
      ENABLE_SSL="$2"; shift 2 ;;
    --email)
      LETSENCRYPT_EMAIL="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 2
      ;;
  esac
done

init_sudo() {
  if [[ ${EUID:-$(id -u)} -eq 0 ]]; then
    SUDO=""
    return 0
  fi

  if ! command -v sudo >/dev/null 2>&1; then
    echo "ERROR: sudo is required (or run as root)." >&2
    exit 1
  fi

  # Validate sudo once up front (may prompt).
  sudo -v
  SUDO="sudo"
}

has_cmd() { command -v "$1" >/dev/null 2>&1; }

install_docker_ubuntu() {
  if has_cmd docker && docker compose version >/dev/null 2>&1; then
    echo "Docker + docker compose already installed."
    return 0
  fi

  if ! has_cmd apt-get; then
    echo "ERROR: Only Ubuntu/Debian (apt-get) is supported by this script." >&2
    exit 1
  fi

  echo "Installing Docker Engine + docker compose plugin..."
  $SUDO apt-get update -y
  $SUDO apt-get install -y ca-certificates curl gnupg

  $SUDO install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | $SUDO gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  $SUDO chmod a+r /etc/apt/keyrings/docker.gpg

  local codename arch
  codename="$(. /etc/os-release && echo "${VERSION_CODENAME}")"
  arch="$(dpkg --print-architecture)"

  echo "deb [arch=${arch} signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${codename} stable" \
    | $SUDO tee /etc/apt/sources.list.d/docker.list >/dev/null

  $SUDO apt-get update -y
  $SUDO apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

  if has_cmd systemctl; then
    $SUDO systemctl enable docker || true
    $SUDO systemctl start docker || true
  fi

  docker --version
  docker compose version
}

install_nginx() {
  if ! has_cmd apt-get; then
    echo "ERROR: Only Ubuntu/Debian (apt-get) is supported by this script." >&2
    exit 1
  fi

  if ! has_cmd nginx; then
    echo "Installing Nginx..."
    $SUDO apt-get update -y
    $SUDO apt-get install -y nginx
  fi

  if has_cmd systemctl; then
    $SUDO systemctl enable nginx || true
    $SUDO systemctl start nginx || true
  fi
}

render_nginx_template() {
  if [[ -z "$DOMAIN" ]]; then
    echo "ERROR: --domain is required when --setup-nginx" >&2
    exit 2
  fi
  if [[ -z "$NGINX_TEMPLATE" ]]; then
    echo "ERROR: --nginx-template is required when --setup-nginx" >&2
    exit 2
  fi
  if [[ ! -f "$NGINX_TEMPLATE" ]]; then
    echo "ERROR: Nginx template not found: $NGINX_TEMPLATE" >&2
    exit 2
  fi

  if ! has_cmd envsubst; then
    echo "Installing envsubst (gettext-base)..."
    $SUDO apt-get update -y
    $SUDO apt-get install -y gettext-base
  fi

  export DOMAIN FRONTEND_PORT BACKEND_PORT
  envsubst '${DOMAIN} ${FRONTEND_PORT} ${BACKEND_PORT}' < "$NGINX_TEMPLATE"
}

configure_nginx() {
  install_nginx

  local sites_available sites_enabled conf_path
  sites_available="/etc/nginx/sites-available"
  sites_enabled="/etc/nginx/sites-enabled"
  conf_path="${sites_available}/${DOMAIN}"

  $SUDO mkdir -p "$sites_available" "$sites_enabled"

  echo "Writing Nginx config: $conf_path"
  render_nginx_template | $SUDO tee "$conf_path" >/dev/null

  $SUDO ln -sf "$conf_path" "${sites_enabled}/${DOMAIN}"
  $SUDO rm -f "${sites_enabled}/default" || true

  $SUDO nginx -t
  if has_cmd systemctl; then
    $SUDO systemctl reload nginx
  else
    $SUDO nginx -s reload
  fi

  if [[ "$ENABLE_SSL" == "true" ]]; then
    if [[ -z "$LETSENCRYPT_EMAIL" ]]; then
      echo "ERROR: --email is required when --enable-ssl true" >&2
      exit 2
    fi

    echo "Installing certbot + requesting certificate..."
    $SUDO apt-get update -y
    $SUDO apt-get install -y certbot python3-certbot-nginx

    $SUDO certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$LETSENCRYPT_EMAIL"

    $SUDO nginx -t
    if has_cmd systemctl; then
      $SUDO systemctl reload nginx
    else
      $SUDO nginx -s reload
    fi
  fi
}

main() {
  if [[ "$INSTALL_DOCKER" != "true" && "$SETUP_NGINX" != "true" ]]; then
    echo "ERROR: Nothing to do. Provide --install-docker and/or --setup-nginx." >&2
    usage
    exit 2
  fi

  init_sudo

  if [[ "$INSTALL_DOCKER" == "true" ]]; then
    install_docker_ubuntu
  fi

  if [[ "$SETUP_NGINX" == "true" ]]; then
    configure_nginx
  fi

  echo "Done."
}

main
