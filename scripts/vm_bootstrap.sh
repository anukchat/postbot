#!/usr/bin/env bash
set -euo pipefail

# Idempotent VM bootstrap for Postbot deployments.
# - Installs Docker Engine if missing
# - Ensures `docker compose` is available (plugin preferred; falls back to standalone v2 binary)
# - Creates the deploy directory and makes it writable
#
# Usage:
#   sudo -n bash vm_bootstrap.sh --deploy-path /opt/postbot --user ubuntu

DEPLOY_PATH=""
DEPLOY_USER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --deploy-path)
      DEPLOY_PATH="$2"
      shift 2
      ;;
    --user)
      DEPLOY_USER="$2"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$DEPLOY_PATH" || -z "$DEPLOY_USER" ]]; then
  echo "Usage: vm_bootstrap.sh --deploy-path <path> --user <ssh-user>" >&2
  exit 2
fi

if ! sudo -n true 2>/dev/null; then
  echo "ERROR: This bootstrap requires non-interactive sudo (NOPASSWD) or root." >&2
  exit 1
fi

has_cmd() { command -v "$1" >/dev/null 2>&1; }

install_docker() {
  if has_cmd docker; then
    return 0
  fi

  echo "Installing Docker Engine..."
  if has_cmd apt-get; then
    sudo -n apt-get update -y
    sudo -n apt-get install -y ca-certificates curl gnupg
  elif has_cmd yum; then
    sudo -n yum -y install ca-certificates curl
  fi

  curl -fsSL https://get.docker.com | sudo -n sh

  # Ensure service is enabled/started when systemd is present
  if has_cmd systemctl; then
    sudo -n systemctl enable docker || true
    sudo -n systemctl start docker || true
  fi
}

ensure_compose() {
  if docker compose version >/dev/null 2>&1; then
    return 0
  fi

  echo "Ensuring Docker Compose is available..."

  # Prefer distro plugin when possible
  if has_cmd apt-get; then
    sudo -n apt-get update -y
    sudo -n apt-get install -y docker-compose-plugin || true
  fi

  if docker compose version >/dev/null 2>&1; then
    return 0
  fi

  # Fallback: install standalone docker-compose v2 as a CLI plugin
  # Note: this installs to a standard plugin directory for the Docker CLI.
  local arch
  arch="$(uname -m)"
  case "$arch" in
    x86_64|amd64) arch="x86_64" ;;
    aarch64|arm64) arch="aarch64" ;;
    *)
      echo "Unsupported architecture for docker-compose fallback: $arch" >&2
      exit 1
      ;;
  esac

  local version url
  version="v2.24.6"
  url="https://github.com/docker/compose/releases/download/${version}/docker-compose-linux-${arch}"

  echo "Installing docker-compose plugin binary (${version})..."
  sudo -n mkdir -p /usr/local/lib/docker/cli-plugins
  sudo -n curl -fsSL "$url" -o /usr/local/lib/docker/cli-plugins/docker-compose
  sudo -n chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

  docker compose version >/dev/null 2>&1
}

ensure_deploy_dir() {
  echo "Ensuring deploy directory exists: $DEPLOY_PATH"
  sudo -n mkdir -p "$DEPLOY_PATH"
  sudo -n chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_PATH"
}

main() {
  install_docker
  ensure_compose
  ensure_deploy_dir

  echo "Bootstrap complete."
}

main
