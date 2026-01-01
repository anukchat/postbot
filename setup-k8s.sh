#!/bin/bash
set -e

# Postbot Kubernetes Setup Script
# This script helps configure your deployment

echo "🚀 Postbot Kubernetes Setup"
echo ""

# Check if production overlay exists
if [ ! -f "k8s/overlays/production/kustomization.yaml" ]; then
  echo "❌ Error: k8s/overlays/production/kustomization.yaml not found"
  echo "Please run this script from the repository root"
  exit 1
fi

# Get GitHub username
echo "📦 GitHub Configuration"
read -p "Enter your GitHub username (for ghcr.io/USERNAME/postbot): " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
  echo "❌ GitHub username is required"
  exit 1
fi

# Get domain name
echo ""
echo "🌐 Domain Configuration"
read -p "Enter your domain name (e.g., example.com): " DOMAIN

if [ -z "$DOMAIN" ]; then
  echo "❌ Domain name is required for production deployment"
  exit 1
fi

# Update production kustomization with GitHub username
echo ""
echo "📝 Updating production configuration..."

# macOS vs Linux sed compatibility
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_INPLACE="sed -i ''"
else
  SED_INPLACE="sed -i"
fi

# Update GitHub username in production kustomization
sed -i '' "s|YOUR_GITHUB_USERNAME|${GITHUB_USERNAME}|g" k8s/overlays/production/kustomization.yaml

# Update domain in production ingress patch
sed -i '' "s|YOUR_DOMAIN.com|${DOMAIN}|g" k8s/overlays/production/ingress-patch.yaml

# Update GitHub username in base kustomization (for reference)
sed -i '' "s|YOUR_GITHUB_USERNAME|${GITHUB_USERNAME}|g" k8s/base/kustomization.yaml

echo ""
echo "✅ Configuration updated!"
echo ""
echo "📋 Summary:"
echo "  GitHub Registry: ghcr.io/${GITHUB_USERNAME}"
echo "  Production Domain: ${DOMAIN}"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure GitHub Secrets (in repository Settings → Secrets):"
echo "   - KUBECONFIG: Your cluster kubeconfig (base64 encoded)"
echo "   - All app secrets (DATABASE_URL, AUTH_PROVIDER_URL, etc.)"
echo ""
echo "2. For local development:"
echo "   make local-all"
echo ""
echo "3. For production deployment:"
echo "   git add k8s/"
echo "   git commit -m 'Configure for production'"
echo "   git push origin main"
echo ""
echo "📚 Documentation: See README.md (Production Deployment section)"
