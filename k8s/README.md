# PostBot - Simple Kubernetes Setup

## Philosophy

**Production-standard patterns, $0 cost, no complexity.**

- ✅ Plain Kubernetes YAML (no Helm)
- ✅ Runs locally with Kind (free)
- ✅ Same files work in production
- ✅ Simple to understand and modify

## Quick Start

### Prerequisites

```bash
# Install Kind (Kubernetes in Docker)
brew install kind

# Install kubectl
brew install kubectl

# Optional: Install k9s (terminal UI for K8s)
brew install k9s
```

### Start Local Cluster

```bash
# 1. Create cluster
kind create cluster --name postbot --config k8s/local/kind-config.yaml

# 2. Build and load images
docker build -f Dockerfile.frontend -t postbot-frontend:local .
docker build -f Dockerfile.backend -t postbot-backend:local .
kind load docker-image postbot-frontend:local --name postbot
kind load docker-image postbot-backend:local --name postbot

# 3. Create namespace and secrets
kubectl apply -f k8s/base/namespace.yaml
kubectl create secret generic postbot-secrets \
  --from-env-file=.env \
  --namespace=postbot

# 4. Deploy everything
kubectl apply -f k8s/base/

# 5. Access application
kubectl port-forward -n postbot service/frontend 3000:3000 &
kubectl port-forward -n postbot service/backend 8000:8000 &

# Visit: http://localhost:3000
```

### Stop Everything

```bash
kind delete cluster --name postbot
```

## Directory Structure

```
k8s/
├── README.md                    # This file
├── base/                        # Production-ready manifests
│   ├── namespace.yaml          # Namespace definition
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── ingress.yaml            # For production with domain
│   └── configmap.yaml          # Non-sensitive config
└── local/
    ├── kind-config.yaml        # Local cluster config
    └── local-ingress.yaml      # Local ingress (optional)
```

## Development Workflow

### Make Changes and Update

```bash
# Rebuild image
docker build -f Dockerfile.backend -t postbot-backend:local .

# Load into Kind
kind load docker-image postbot-backend:local --name postbot

# Restart deployment
kubectl rollout restart deployment/backend -n postbot

# Watch logs
kubectl logs -f deployment/backend -n postbot
```

### Debug

```bash
# Check pods
kubectl get pods -n postbot

# Get pod logs
kubectl logs -f <pod-name> -n postbot

# Shell into pod
kubectl exec -it <pod-name> -n postbot -- /bin/sh

# Check events
kubectl get events -n postbot --sort-by='.lastTimestamp'
```

## Deploying to Production (Free Tier Options)

### Option 1: Oracle Cloud Free Tier
- 2 AMD VMs (1/8 OCPU, 1GB RAM each)
- Install k3s
- Use same YAML files
- **Cost: $0 forever**

### Option 2: AWS Free Tier (12 months)
- t2.micro EC2 instance
- Install k3s
- Use same YAML files
- **Cost: $0 for 1 year**

### Option 3: Google Cloud Free Tier
- e2-micro VM
- Install k3s
- Use same YAML files
- **Cost: $0 with free credits**

## Production Deployment

```bash
# 1. SSH into server
ssh ubuntu@your-server

# 2. Install k3s
curl -sfL https://get.k3s.io | sh -

# 3. Copy kubeconfig
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER ~/.kube/config

# 4. Clone repo
git clone https://github.com/yourusername/postbot.git
cd postbot

# 5. Create secrets
kubectl create secret generic postbot-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=AUTH_PROVIDER_URL="$AUTH_PROVIDER_URL" \
  # ... add all secrets

# 6. Deploy
kubectl apply -f k8s/base/

# 7. Setup ingress with your domain
kubectl apply -f k8s/production/ingress.yaml
```

## Why Plain YAML Instead of Helm?

**Helm Pros:**
- Templating for multiple environments
- Package management
- Popular in enterprises

**Plain YAML Pros:**
- ✅ Simpler to understand
- ✅ No new tool to learn
- ✅ Direct control
- ✅ Easy to debug
- ✅ Better for small projects
- ✅ Can use Kustomize later if needed

**For PostBot:** Plain YAML is perfect. Add Helm only when you have 10+ services.

## Scaling

```bash
# Scale manually
kubectl scale deployment backend --replicas=5 -n postbot

# Auto-scale (add HPA later)
kubectl autoscale deployment backend \
  --cpu-percent=70 \
  --min=2 --max=10 \
  -n postbot
```

## Adding New Services

Just create new YAML files:

```bash
# Add Redis
cat > k8s/base/redis-deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: postbot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
EOF

kubectl apply -f k8s/base/redis-deployment.yaml
```

## Monitoring (Optional, Still Free)

```bash
# Install Prometheus + Grafana
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml

# Or use k9s for terminal monitoring
k9s
```

## Cost Comparison

| Setup | Monthly Cost | Where | Specs |
|-------|--------------|-------|-------|
| **Kind (Local)** | $0 | Your laptop | Full K8s |
| **Oracle Cloud** | $0 | Cloud | 2 VMs, k3s |
| **AWS Free Tier** | $0 (1 yr) | Cloud | t2.micro, k3s |
| **DigitalOcean** | $4 | Cloud | 1GB RAM, k3s |
| **Linode** | $5 | Cloud | 1GB RAM, k3s |

## Tools Cheatsheet

```bash
# Kind
kind create cluster --name postbot
kind load docker-image myimage:latest --name postbot
kind delete cluster --name postbot

# kubectl
kubectl get pods -n postbot
kubectl logs -f pod/backend-xxx -n postbot
kubectl exec -it pod/backend-xxx -n postbot -- sh
kubectl port-forward svc/frontend 3000:3000 -n postbot

# k9s (terminal UI)
k9s -n postbot
```

## Next Steps

1. **Try locally first**: `kind create cluster`
2. **Test everything**: Make sure app works in K8s
3. **Pick free tier**: Oracle Cloud / AWS / GCP
4. **Deploy**: Same YAML files work everywhere

Questions? Check the YAML files - they're self-documenting!
