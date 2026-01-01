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
## 🚀 Production Deployment (Docker Compose on a VM)

This repo keeps Kubernetes manifests for **local demo/learning**, but the recommended production deployment path is **Docker Compose** on a single VM (OCI/AWS/etc).

### Option A: Manual deploy on a VM

1. Provision a VM (Ubuntu 22.04 is fine) and install:
    - Docker + Docker Compose plugin
2. Copy `docker-compose.yml` to the VM.
3. Create a `.env` on the VM (start from `.env.template`).
4. Run:

```bash
docker compose pull
docker compose up -d --remove-orphans
```

### Option B: Automatic deploy from GitHub Actions (recommended)

This repo keeps the production automation simple:

1) **One-time VM setup (manual trigger):** installs Docker + Docker Compose, and can optionally configure Nginx + HTTPS.
    - Workflow: [.github/workflows/bootstrap.yml](.github/workflows/bootstrap.yml)
2) **Deploy on every push to `main`:** builds and pushes images to GHCR, then SSHes into your VM to run `docker compose pull && docker compose up`.
    - Workflow: [.github/workflows/deploy.yml](.github/workflows/deploy.yml)

#### GitHub Secrets you must set

| Secret | Required | Used by | Notes |
|---|---:|---|---|
| `DEPLOY_HOST` | yes | bootstrap + deploy | VM public IP / DNS |
| `DEPLOY_USER` | yes | bootstrap + deploy | SSH user (e.g. `ubuntu`) |
| `DEPLOY_PORT` | yes | bootstrap + deploy | Usually `22` |
| `DEPLOY_SSH_KEY` | yes | bootstrap + deploy | Private key contents |
| `DEPLOY_PATH` | yes | bootstrap + deploy | Recommend under SSH home (e.g. `/home/ubuntu/postbot`) |
| `POSTBOT_ENV` | yes | deploy | Multiline secret = VM `.env` contents |
| `GHCR_USERNAME` | maybe | deploy | Needed only if GHCR images are private |
| `GHCR_PAT` | maybe | deploy | PAT with `read:packages` |
| `SUPABASE_URL` | yes | build | Frontend build arg |
| `SUPABASE_KEY` | yes | build | Frontend build arg |
| `AUTH_PROVIDER_URL` | yes | build | Frontend build arg |
| `AUTH_PROVIDER_KEY` | yes | build | Frontend build arg |
| `API_URL` | yes | build | Frontend build arg |
| `REDIRECT_URL` | yes | build | Frontend build arg |
| `DEPLOY_DOMAIN` | no | bootstrap | Only if configuring Nginx |
| `LETSENCRYPT_EMAIL` | no | bootstrap | Only if enabling HTTPS |

**1) VM SSH (required):**
```bash
DEPLOY_HOST=your.server.ip.or.hostname
DEPLOY_USER=ubuntu
DEPLOY_PORT=22
DEPLOY_SSH_KEY=<private key with access to the server>
# Tip: prefer a path under the SSH user's home to avoid needing sudo
DEPLOY_PATH=/home/ubuntu/postbot
```

**1b) Nginx/TLS (optional, used by the bootstrap workflow):**
```bash
DEPLOY_DOMAIN=postbot.yourdomain.com
LETSENCRYPT_EMAIL=you@yourdomain.com
```

**2) Runtime env (required):**
Store your `.env` file contents as a single multiline secret:
```bash
POSTBOT_ENV=<contents of your .env file>
```

**3) GHCR pull auth (required if images are private):**
```bash
GHCR_USERNAME=your-github-username
GHCR_PAT=<a GitHub PAT with read:packages>
```

**4) Frontend build args (only for your deployment):**
These are used when building the frontend image in CI:
```bash
SUPABASE_URL=...
SUPABASE_KEY=...
AUTH_PROVIDER_URL=...
AUTH_PROVIDER_KEY=...
API_URL=...
REDIRECT_URL=...
```

## ⚡ Quick Start (10 minutes)

This is the simplest way to run PostBot locally.

**Prereqs:** Docker + Docker Compose.

> Want the local Kubernetes (Kind) demo instead? See [k8s/README.md](k8s/README.md).

### 1. Set Up Database

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

### 2. Add at Least One LLM API Key

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

### 3. Run Locally

Create your local environment file:

```bash
cp .env.template .env
```

Start the app:

```bash
docker compose -f docker-compose.local.yml up --build
```

### 4. Access Your Application

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
docker compose -f docker-compose.local.yml down
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
| **Infrastructure** | Docker, Docker Compose, GitHub Actions, GHCR (optional Nginx) |

### Key Features

- **Pluggable Authentication**: Switch between Supabase, Auth0, or Clerk
- **Multi-LLM Support**: Automatically falls back if primary LLM fails
- **Agentic Workflow**: LangGraph agents for intelligent content generation
- **Vector Search**: Semantic search using Qdrant embeddings
- **Production-Ready**: Health checks and repeatable deployments

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
├── docker-compose.local.yml  # Local dev (Docker Compose)
├── docker-compose.yml        # Production deploy (Docker Compose on VM)
└── .env.template       # Environment template
```

### Useful Commands

```bash
# Local (Docker Compose)
docker compose -f docker-compose.local.yml up --build
docker compose -f docker-compose.local.yml logs -f
docker compose -f docker-compose.local.yml down

# Local Kubernetes demo (optional)
# See: k8s/README.md

# Database
alembic upgrade head  # Run migrations
alembic history       # View history
alembic current       # Current version
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
cp .env.template .env
docker compose -f docker-compose.local.yml up --build

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
<summary><b>Containers won't start</b></summary>

```bash
# Check container logs
docker compose -f docker-compose.local.yml ps
docker logs postbot-backend-local --tail 200
docker logs postbot-frontend-local --tail 200

# Common issues:
# 1. Missing env vars
# Ensure .env exists and includes DATABASE_URL and auth vars

# 2. Database connection
# Verify DATABASE_URL is correct and database is accessible

# If you're using the optional local Kubernetes demo, see k8s/README.md.
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
docker exec -it postbot-backend-local env | grep AUTH

# Check CORS settings match your domain
docker exec -it postbot-backend-local env | grep ALLOWED_ORIGINS

# If you're using the optional local Kubernetes demo, see k8s/README.md.
```

</details>

<details>
<summary><b>LLM API calls failing</b></summary>

```bash
# Check API keys are set
docker exec -it postbot-backend-local env | grep API_KEY

# Test API key manually
curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/v1/models

# Check logs for specific error
docker logs postbot-backend-local --tail 200 | grep -i error

# If you're using the optional local Kubernetes demo, see k8s/README.md.
```

</details>

<details>
<summary><b>Images not pulling from GHCR</b></summary>

```bash
# For VM deploys (Docker Compose), images pull via `docker login`.
# Ensure GHCR packages are public, OR set GHCR_USERNAME/GHCR_PAT secrets.
# Then re-run the deploy workflow.
```

</details>

<details>
<summary><b>Frontend shows "Cannot connect to server"</b></summary>

```bash
# Check containers are running
docker compose -f docker-compose.local.yml ps

# Check backend logs
docker logs postbot-backend-local --tail 200

# Check VITE_API_URL in your .env matches where backend is exposed
# (default in docker-compose.local.yml is http://localhost:8000)
```

</details>

<details>
<summary><b>SSL certificate not issuing</b></summary>

```bash
# If you used the VM bootstrap workflow with Nginx/certbot:
sudo nginx -t
sudo systemctl status nginx
sudo certbot certificates

# DNS must be pointing to your VM
dig yourdomain.com

# Also ensure ports 80/443 are open in your firewall/security group.

# If you're using the optional local Kubernetes demo, see k8s/README.md.
```

</details>

### Still Stuck?

1. **Check Logs**: `docker logs postbot-backend-local --tail 200`
2. **Check Status**: `docker compose -f docker-compose.local.yml ps`
3. **Open Issue**: [GitHub Issues](https://github.com/your-username/postbot/issues) with:
   - Steps to reproduce
   - Error messages
    - Environment (local/production)

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