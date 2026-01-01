<div align="center">

# 🚀 POST BOT

### Transform Your Tweets into Engaging Blog Content with AI

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg?logo=react)](https://reactjs.org/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-326CE5.svg?logo=kubernetes)](https://kubernetes.io/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**[Quick Start](#-quick-start-10-minutes)** • **[Features](#-features)** • **[Architecture](#-architecture)** • **[Production Deployment](#-production-deployment)** • **[Contributing](#-contributing)**

</div>

---

## 📖 What is POST BOT?

POST BOT is an **AI-powered content generation platform** that helps you create professional blog posts from Twitter bookmarks. Just import your bookmarks, and POST BOT will:

✨ Extract tweets and analyze embedded content (GitHub repos, PDFs, articles)  
🤖 Use AI agents (powered by LangGraph) to generate well-structured blog posts  
🎨 Support multiple writing styles and personas  
📊 Store and manage your content with full-text search  

**Perfect for:**
- 📝 Content creators who bookmark interesting tweets
- 🎓 Researchers documenting Twitter threads
- 💼 Teams creating content from social media trends
- 🚀 Anyone wanting to turn Twitter insights into blogs

**Key Features:**
- 🚢 **Production-ready:** Kubernetes deployment with auto-scaling
- 🔒 **Flexible Auth:** Choose Supabase, Auth0, or Clerk
- 🤖 **Multi-LLM:** OpenAI, Claude, Gemini, Groq with smart fallbacks
- 📊 **Robust Storage:** PostgreSQL + Qdrant vector database
- ⚡ **Auto-deploy:** Push to GitHub → Deployed automatically

---

## 🚀 Quick Start (10 Minutes)

Get POST BOT running locally in just 3 commands:

### Prerequisites

**Required:**
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (running)
- [kubectl](https://kubernetes.io/docs/tasks/tools/) installed
- **5GB free RAM** and **20GB free disk space**

**For authentication, choose ONE:**
- [Supabase](https://supabase.com/) account (recommended - free tier) 
- [Auth0](https://auth0.com/) account (enterprise features)
- [Clerk](https://clerk.com/) account (modern UI)

### 1. Clone and Configure

```bash
# Clone repository
git clone https://github.com/yourusername/postbot.git
cd postbot

# Copy environment template
cp .env.template .env.local

# Edit with your credentials (see Authentication section below)
nano .env.local  # or use your favorite editor
```

### 2. Set Up Authentication

<details>
<summary><b>Option A: Supabase (Recommended)</b></summary>

```bash
# In .env.local, set:
AUTH_PROVIDER=supabase
VITE_SUPABASE_URL=https://YOUR-PROJECT.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_URL=https://YOUR-PROJECT.supabase.co
SUPABASE_KEY=your-service-role-key-here
```

**Get credentials:**
1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Go to Settings → API → Copy URL and keys

</details>

<details>
<summary><b>Option B: Auth0</b></summary>

```bash
# In .env.local, set:
AUTH_PROVIDER=auth0
VITE_AUTH0_DOMAIN=your-tenant.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-secret
```

**Get credentials:**
1. Create account at [auth0.com](https://auth0.com)
2. Create Application → Single Page Application
3. Copy Domain, Client ID, and Secret

</details>

<details>
<summary><b>Option C: Clerk</b></summary>

```bash
# In .env.local, set:
AUTH_PROVIDER=clerk
VITE_CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx
```

**Get credentials:**
1. Create account at [clerk.com](https://clerk.com)
2. Create Application
3. Copy Publishable Key and Secret Key

</details>

### 3. Set Up Database

**Easy Option** - Use Supabase (free PostgreSQL):
```bash
# In .env.local, add:
DATABASE_URL=postgresql://postgres.[project]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
```

<details>
<summary><b>Alternative: Local PostgreSQL</b></summary>

```bash
# Install PostgreSQL (macOS)
brew install postgresql@14
brew services start postgresql@14

# Create database
createdb postbot_dev

# In .env.local:
DATABASE_URL=postgresql://your_username@localhost:5432/postbot_dev
```

</details>

### 4. Add at Least One LLM API Key

```bash
# In .env.local, add at least ONE of these:
GROQ_API_KEY=your-groq-key        # Recommended - fast & free tier
GEMINI_API_KEY=your-gemini-key    # Google Gemini
OPENROUTER_API_KEY=your-key       # Access multiple models
DEEPSEEK_API_KEY=your-key         # DeepSeek
```

**Get free keys:**
- **Groq** (recommended): [console.groq.com](https://console.groq.com)
- **Gemini**: [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

### 5. Run Everything

```bash
# One command to rule them all! 🎉
make local-all
```

**This will:**
1. Create local Kubernetes cluster (Kind)
2. Build Docker images
3. Deploy backend + frontend
4. Run database migrations
5. Forward ports for access

**Wait 2-3 minutes** for everything to start...

### 6. Access Your Application

Once deployment is complete:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

**First-time setup:**
1. Open http://localhost:3000
2. Click "Login" → Authenticate with your provider
3. Start uploading Twitter bookmarks!

### 🛑 Stop Everything

```bash
make local-clean  # Stops and removes everything
```

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🐦 Smart Content Extraction
- Automated tweet collection from bookmarks
- Reference detection (GitHub, PDFs, HTML)
- Media and metadata extraction
- Document intelligence processing

</td>
<td width="50%">

### 🤖 AI-Powered Generation
- Multi-LLM support with fallback
- Multiple writing styles & personas
- Agentic workflow with LangGraph
- Real-time content preview

</td>
</tr>
<tr>
<td width="50%">

### 💾 Enterprise Storage
- PostgreSQL with SQLAlchemy
- Qdrant vector database
- Semantic search capabilities
- Automatic embeddings generation

</td>
<td width="50%">

### 🎨 Modern Interface
- React 18+ with TypeScript
- Responsive design
- Real-time updates
- OAuth2 authentication

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User's Browser                            │
│                   (React 18 + TypeScript)                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                           │
│                                                                   │
│    ┌──────────────┐         ┌──────────────┐                   │
│    │   Frontend   │         │   Backend    │                   │
│    │   (Nginx)    │◄────────┤   (FastAPI)  │                   │
│    │  Replicas: 2 │         │  Replicas: 2 │                   │
│    └──────────────┘         └──────┬───────┘                   │
│                                     │                            │
└─────────────────────────────────────┼────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
        ┌───────────────┐  ┌──────────────┐  ┌─────────────┐
        │  PostgreSQL   │  │    Qdrant    │  │  LLM APIs   │
        │  (Your DB)    │  │  Vector DB   │  │  (External) │
        └───────────────┘  └──────────────┘  └─────────────┘
```

### Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS |
| **Backend** | FastAPI, Python 3.12+, LangGraph agents |
| **Database** | PostgreSQL (any provider), Qdrant vector DB |
| **Auth** | Supabase / Auth0 / Clerk (pluggable) |
| **LLMs** | OpenAI, Claude, Gemini, Groq (with fallbacks) |
| **Infrastructure** | Kubernetes, Docker, GitHub Actions, GHCR |

### Key Features

- **Pluggable Authentication**: Switch between Supabase, Auth0, or Clerk
- **Multi-LLM Support**: Automatically falls back if primary LLM fails
- **Agentic Workflow**: LangGraph agents for intelligent content generation
- **Vector Search**: Semantic search using Qdrant embeddings
- **Production-Ready**: Health checks, auto-scaling, zero-downtime deploys

---

## 🚀 Production Deployment

Deploy POST BOT to production with **automated CI/CD** on every git push.

### Prerequisites

**Required:**
- Kubernetes cluster (GKE, EKS, AKS, or DigitalOcean)
- Domain name with DNS access
- GitHub account (for Actions)

**Cost-Effective Options:**
- **Free Tier**: Oracle Cloud (永久免费 24GB RAM)
- **Low Cost**: DigitalOcean ($12/month), Linode ($10/month)
- **Managed**: GKE, EKS, AKS ($70+/month)

### One-Time Setup

#### 1. Configure Your Deployment

```bash
# Run setup script
./setup-k8s.sh

# Prompts:
# - GitHub username: your-username
# - Domain: yourdomain.com
```

This updates:
- `k8s/overlays/production/kustomization.yaml` → Your GitHub registry
- `k8s/overlays/production/ingress-patch.yaml` → Your domain

#### 2. Set Up GitHub Secrets

Go to **GitHub Repository → Settings → Secrets → Actions** and add:

<details>
<summary><b>Required Secrets (Click to expand)</b></summary>

**Kubernetes:**
```bash
KUBECONFIG=<base64-encoded-kubeconfig>
```

**Database:**
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

**Authentication** (choose one):
```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# OR Auth0
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-secret

# OR Clerk
CLERK_SECRET_KEY=sk_live_xxx
CLERK_PUBLISHABLE_KEY=pk_live_xxx
```

**LLM APIs** (at least one):
```bash
GROQ_API_KEY=your-key
GEMINI_API_KEY=your-key
OPENROUTER_API_KEY=your-key
```

**URLs:**
```bash
API_URL=https://yourdomain.com/api
FRONTEND_URL=https://yourdomain.com
REDIRECT_URL=https://yourdomain.com/app
```

</details>

<details>
<summary><b>Optional Secrets</b></summary>

```bash
REDDIT_CLIENT_ID=your-id
REDDIT_CLIENT_SECRET=your-secret
REDDIT_USER_AGENT=postbot:v1.0.0
SERPER_API_KEY=your-key
PIXABAY_API_KEY=your-key
```

</details>

#### 3. Deploy

```bash
git add .
git commit -m "Configure for production"
git push origin main
```

**That's it!** GitHub Actions will:
1. ✅ Build Docker images
2. ✅ Push to GitHub Container Registry
3. ✅ Create/update Kubernetes secrets
4. ✅ Deploy to your cluster
5. ✅ Wait for rollout completion
6. ✅ Verify deployment

**Monitor deployment:**
```bash
# Watch progress
kubectl get pods -n postbot -w

# Check logs
kubectl logs -f deployment/backend -n postbot
kubectl logs -f deployment/frontend -n postbot
```

### SSL Certificate (Automatic)

POST BOT uses **cert-manager** for automatic SSL:

```bash
# Install cert-manager (one-time)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Certificate will be issued automatically
# Check status:
kubectl get certificate -n postbot
```

### Post-Deployment

**Verify everything works:**
```bash
# Check all pods are running
kubectl get pods -n postbot

# Check ingress
kubectl get ingress -n postbot

# Test endpoints
curl https://yourdomain.com/api/health
curl https://yourdomain.com
```

**Access your app:**
1. Open https://yourdomain.com
2. Login with your auth provider
3. Start creating content!

### Updating

Just push to main branch:
```bash
git push origin main  # Auto-deploys! 🚀
```

**Zero-downtime updates:**
- Old pods kept running until new ones are ready
- Automatic rollback if health checks fail

---

## ⚙️ Configuration

### Environment Variables Reference

<details>
<summary><b>Database & Core</b></summary>

```env
# Database (Required)
DATABASE_URL=postgresql://user:password@host:5432/database

# Application URLs
API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Environment
ENVIRONMENT=development  # or production
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
```

</details>

<details>
<summary><b>Authentication (Choose One)</b></summary>

**Supabase:**
```env
AUTH_PROVIDER=supabase
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
```

**Auth0:**
```env
AUTH_PROVIDER=auth0
VITE_AUTH0_DOMAIN=your-tenant.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-secret
```

**Clerk:**
```env
AUTH_PROVIDER=clerk
VITE_CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx
```

</details>

<details>
<summary><b>LLM APIs</b></summary>

```env
# Add at least one
GROQ_API_KEY=gsk_xxx              # Recommended - fast & free
GEMINI_API_KEY=xxx                # Google Gemini
OPENROUTER_API_KEY=sk-or-xxx      # Multiple models
DEEPSEEK_API_KEY=xxx              # DeepSeek
OLLAMA_API_KEY=xxx                # Local models
```

</details>

<details>
<summary><b>Optional Services</b></summary>

```env
# Reddit API
REDDIT_CLIENT_ID=your-id
REDDIT_CLIENT_SECRET=your-secret
REDDIT_USER_AGENT=postbot:v1.0.0

# Search & Images
SERPER_API_KEY=your-key           # Google search
PIXABAY_API_KEY=your-key          # Free images
```

</details>

### Database Migrations

POST BOT uses Alembic for database schema management:

```bash
# Run migrations (creates all tables + seeds data)
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Rollback one version
alembic downgrade -1

# View migration history
alembic history
```

**What gets created:**
- 31 application tables (users, content, sources, templates, etc.)
- 3 LangGraph checkpoint tables (for agent state)
- Reference data (content types, source types, parameters)

---

## 📱 Usage

### Import Twitter Bookmarks

1. Export from Twitter: **Bookmarks → More → Download**
2. Upload JSON file to POST BOT
3. Wait for extraction (analyzes all embedded content)
4. Review extracted content

### Generate Blog Posts

1. Select one or more tweets
2. Choose writing style:
   - 📝 Technical / Tutorial
   - 🎯 Professional / Business
   - 😊 Casual / Friendly
   - 🎓 Academic / Research
3. Click "Generate"
4. AI agent will:
   - Analyze content and references
   - Research related topics
   - Create structured outline
   - Generate full blog post
5. Review and edit in built-in editor
6. Export as Markdown, PDF, or DOCX

### API Usage

```python
import requests

# API base URL
api_url = "http://localhost:8000/api"
headers = {"Authorization": f"Bearer {your_token}"}

# Upload tweets
response = requests.post(
    f"{api_url}/sources",
    json={"type": "twitter", "data": tweet_data},
    headers=headers
)

# Generate content
response = requests.post(
    f"{api_url}/content/generate",
    json={
        "source_ids": ["uuid-1", "uuid-2"],
        "template_id": "uuid-3",
        "parameters": {"style": "technical", "tone": "professional"}
    },
    headers=headers
)

content_id = response.json()["content_id"]

# Get generated content
response = requests.get(f"{api_url}/content/{content_id}", headers=headers)
print(response.json()["generated_text"])
```

**API Documentation:** Visit `/docs` for interactive Swagger UI

---

## 🛠️ Development

### Manual Run (Without Kubernetes)

**Backend:**
```bash
cd src/backend

# Install dependencies
pip install -r requirements.txt -r requirements_llm.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn api.api:app --reload --port 8000
```

**Frontend:**
```bash
cd src/frontend/project

# Install dependencies
npm install

# Start dev server
npm run dev
```

Access:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Project Structure

```
postbot/
├── .github/workflows/    # CI/CD pipelines
├── alembic/             # Database migrations
├── k8s/                 # Kubernetes manifests
│   ├── base/            # Base configs
│   └── overlays/        # Environment-specific
├── src/
│   ├── backend/
│   │   ├── agents/      # LangGraph AI agents
│   │   ├── api/         # FastAPI endpoints
│   │   ├── auth/        # Authentication providers
│   │   ├── db/          # Database models & repos
│   │   └── extraction/  # Content extractors
│   └── frontend/
│       └── project/     # React application
├── Makefile            # Development commands
├── docker-compose.yml  # Local testing
└── .env.template       # Environment template
```

### Useful Commands

```bash
# Kubernetes (Local)
make local-all        # Start everything
make logs             # View all logs
make logs-backend     # Backend logs only
make logs-frontend    # Frontend logs only
make status          # Cluster status
make local-clean     # Stop and cleanup

# Docker Compose
docker-compose up -d  # Start services
docker-compose logs -f # View logs
docker-compose down   # Stop services

# Database
alembic upgrade head  # Run migrations
alembic history       # View history
alembic current       # Current version

# Build
make build ENV=local  # Build Docker images
```

---

## 🤝 Contributing

We love contributions! POST BOT is open source and welcomes improvements from the community.

### Quick Start for Contributors

```bash
# Fork and clone
git clone https://github.com/your-username/postbot.git
cd postbot

# Create feature branch
git checkout -b feature/your-feature

# Make changes and test locally
make local-all

# Commit and push
git commit -m "Add your feature"
git push origin feature/your-feature

# Open Pull Request on GitHub
```

### Contribution Guidelines

- **Code Style**: Follow existing patterns, use type hints
- **Testing**: Add tests for new features
- **Documentation**: Update README if adding features
- **Commits**: Use clear, descriptive commit messages
- **PR Description**: Explain what and why, not just how

### Areas We Need Help

- 🧪 **Testing**: Unit tests, integration tests
- 📝 **Documentation**: Tutorials, examples
- 🐛 **Bug Fixes**: Check issues labeled `good first issue`
- ✨ **Features**: Check roadmap below

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details.

---

## 🐛 Troubleshooting

<details>
<summary><b>Pods won't start / CrashLoopBackOff</b></summary>

```bash
# Check pod logs
kubectl logs -f deployment/backend -n postbot

# Common issues:
# 1. Missing secrets
kubectl get secrets -n postbot
kubectl describe secret postbot-secrets -n postbot

# 2. Database connection
# Verify DATABASE_URL is correct and database is accessible

# 3. Resource limits
kubectl describe pod -n postbot  # Check resource requests
```

</details>

<details>
<summary><b>Cannot connect to database</b></summary>

```bash
# Test database connection
psql "$DATABASE_URL"

# If using Supabase, ensure:
# 1. Database pooler is used (6543 port with session mode)
# 2. IP allowlist includes your cluster IPs
# 3. SSL mode is required in connection string

# Connection string format:
# postgresql://postgres.[project]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
```

</details>

<details>
<summary><b>Authentication not working</b></summary>

```bash
# Check frontend can reach auth provider
curl -v https://your-project.supabase.co

# Verify environment variables
kubectl exec -it deployment/backend -n postbot -- env | grep AUTH

# Check CORS settings match your domain
kubectl exec -it deployment/backend -n postbot -- env | grep ALLOWED_ORIGINS
```

</details>

<details>
<summary><b>LLM API calls failing</b></summary>

```bash
# Check API keys are set
kubectl exec -it deployment/backend -n postbot -- env | grep API_KEY

# Test API key manually
curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/v1/models

# Check logs for specific error
kubectl logs -f deployment/backend -n postbot | grep -i error
```

</details>

<details>
<summary><b>Images not pulling from GHCR</b></summary>

```bash
# Ensure images are public or create imagePullSecret
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=your-github-username \
  --docker-password=your-github-token \
  --namespace=postbot

# Add to deployment:
# spec.template.spec.imagePullSecrets:
#   - name: ghcr-secret
```

</details>

<details>
<summary><b>Frontend shows "Cannot connect to server"</b></summary>

```bash
# Check backend is running
kubectl get pods -n postbot

# Verify ingress routing
kubectl get ingress -n postbot
kubectl describe ingress postbot-ingress -n postbot

# Check API URL in frontend
kubectl exec -it deployment/frontend -n postbot -- cat /usr/share/nginx/html/env.js
```

</details>

<details>
<summary><b>SSL certificate not issuing</b></summary>

```bash
# Check cert-manager is installed
kubectl get pods -n cert-manager

# Check certificate status
kubectl get certificate -n postbot
kubectl describe certificate postbot-tls -n postbot

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# DNS must be pointing to your cluster
dig yourdomain.com
```

</details>

### Still Stuck?

1. **Check Logs**: `kubectl logs -f deployment/backend -n postbot`
2. **Describe Resources**: `kubectl describe pod -n postbot`
3. **Open Issue**: [GitHub Issues](https://github.com/your-username/postbot/issues) with:
   - Steps to reproduce
   - Error messages
   - Environment (local/production, K8s version)

---

## 📋 Roadmap

### Short Term (Q1 2026)
- [ ] Add comprehensive test suite (70% coverage)
- [ ] Performance monitoring dashboard
- [ ] Database query optimization
- [ ] Frontend bundle size reduction

### Medium Term (Q2 2026)
- [ ] LinkedIn content extraction support
- [ ] Reddit threads support
- [ ] Additional LLM providers (Anthropic Claude)
- [ ] Webhook notifications for completed generations
- [ ] WordPress/Ghost integration

### Long Term (Q3-Q4 2026)
- [ ] Browser extension (Chrome/Firefox)
- [ ] Mobile app (React Native)
- [ ] Team collaboration features
- [ ] Advanced analytics dashboard
- [ ] Multi-language content generation
- [ ] Voice-over generation

**Want to help?** Check [Contributing](#-contributing) section!

---

## 📄 License

GNU General Public License v3.0 - see [LICENSE](LICENSE) for details.

**What this means:**
- ✅ Use commercially
- ✅ Modify and distribute
- ✅ Use privately
- ⚠️ Must disclose source
- ⚠️ Must use same license for derivatives
- ⚠️ State changes made

---

## 🙏 Acknowledgments

POST BOT is built on the shoulders of giants:

- **AI/ML**: [LangChain](https://langchain.com/), [LangGraph](https://langchain-ai.github.io/langgraph/)
- **Vector Search**: [Qdrant](https://qdrant.tech/)
- **Frontend**: [React](https://react.dev/), [Tailwind CSS](https://tailwindcss.com/)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/)
- **Infrastructure**: [Kubernetes](https://kubernetes.io/), [Docker](https://www.docker.com/)

Special thanks to all [contributors](https://github.com/your-username/postbot/graphs/contributors)!

---

## 📬 Support & Community

**Need Help?**
- 📖 Check [Troubleshooting](#-troubleshooting) section
- 🐛 [Open an Issue](https://github.com/your-username/postbot/issues)
- 💬 [GitHub Discussions](https://github.com/your-username/postbot/discussions)

**Stay Updated:**
- ⭐ [Star on GitHub](https://github.com/your-username/postbot)
- 👁️ [Watch Releases](https://github.com/your-username/postbot/releases)
- 🐦 Follow on Twitter: [@postbot](https://twitter.com/postbot) _(coming soon)_

---

<div align="center">

**Built with ❤️ for content creators**

[⭐ Star](https://github.com/your-username/postbot) • [🐛 Report Bug](https://github.com/your-username/postbot/issues) • [💡 Request Feature](https://github.com/your-username/postbot/issues) • [📖 Docs](#-quick-start-10-minutes)

**Made by the POST BOT Team • Licensed under GPLv3**

</div> 