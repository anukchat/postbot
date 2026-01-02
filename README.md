<div align="center">

# 🚀 POST BOT

### Transform Your Tweets into Engaging Blog Content with AI

**Automatically convert your Twitter bookmarks into polished blog posts using cutting-edge AI agents**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg?logo=react)](https://reactjs.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**[🚀 Quick Start](#-quick-start-5-steps)** • **[☁️ Deploy](#-production-deployment)** • **[🎬 Demo](#-demo)** • **[✨ Features](#-features)** • **[🏗️ Architecture](#-architecture)** • **[🤝 Contributing](#-contributing)**

</div>

---

## 🎯 Why POST BOT?

- ✅ **One-Click Blog Generation** - Transform tweets into full blog posts in seconds
- ✅ **AI Agent Workflow** - Powered by LangGraph with intelligent planning and execution
- ✅ **Multi-LLM Support** - Works with Groq, Gemini, OpenAI, and more (with auto-fallback)
- ✅ **Smart Content Extraction** - Automatically analyzes embedded links, PDFs, and GitHub repos
- ✅ **Production Ready** - Docker-based deployment with automated CI/CD
- ✅ **100% Open Source** - Self-host on any cloud or run locally

---

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ **Docker & Docker Compose** ([Install Docker](https://docs.docker.com/get-docker/))
- ✅ **PostgreSQL Database** (we recommend [Supabase](https://supabase.com) - free tier available)
- ✅ **LLM API Key** (at least one):
  - [Groq](https://console.groq.com) (recommended - fast & generous free tier)
  - [Google Gemini](https://makersuite.google.com/app/apikey) (free tier)
  - OpenAI, OpenRouter, or DeepSeek
- ✅ **Auth Provider Account**:
  - [Supabase](https://supabase.com) (easiest - handles auth + database)
  - Or Auth0, Clerk

**Estimated setup time:** 5-10 minutes ⏱️

---

## ⚡ Quick Start (5 Steps)

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/postbot.git
cd postbot
```

### Step 2: Create Environment File

```bash
cp .env.example .env
```

Now edit `.env` and fill in **these required values**:

```bash
# ============================================
# REQUIRED: Database (Supabase recommended)
# ============================================
DATABASE_URL=postgresql://postgres.[PROJECT]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres

# ============================================
# REQUIRED: Authentication (Supabase example)
# ============================================
AUTH_PROVIDER=supabase
SUPABASE_URL=https://[PROJECT].supabase.co
SUPABASE_KEY=your-service-role-key-here

# Frontend needs these too
VITE_SUPABASE_URL=https://[PROJECT].supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here

# ============================================
# REQUIRED: Application URLs
# ============================================
VITE_API_URL=http://localhost:8000
VITE_REDIRECT_URL=http://localhost:3000

# ============================================
# REQUIRED: At least ONE LLM API key
# ============================================
GROQ_API_KEY=gsk_...                    # Recommended (fast & free)
# GEMINI_API_KEY=...                    # Alternative
# OPENROUTER_API_KEY=sk-or-...          # Alternative
```

<details>
<summary>🔍 <b>Where do I get these values?</b></summary>

**Supabase (Database + Auth):**
1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Go to **Settings → Database**:
   - Copy "Connection string" (use **Transaction** pooler mode)
   - This is your `DATABASE_URL`
4. Go to **Settings → API**:
   - Copy "Project URL" → `SUPABASE_URL` and `VITE_SUPABASE_URL`
   - Copy "service_role" key → `SUPABASE_KEY`
   - Copy "anon public" key → `VITE_SUPABASE_ANON_KEY`

**Groq API Key (LLM):**
1. Sign up at [console.groq.com](https://console.groq.com)
2. Go to API Keys section
3. Create new API key
4. Copy to `GROQ_API_KEY`

</details>

### Step 3: Start the Application

```bash
docker compose -f docker-compose.local.yml up --build
```

**Wait for these success messages:**
```
✅ backend  | INFO:     Uvicorn running on http://0.0.0.0:8000
✅ frontend | ➜  Local:   http://localhost:3000/
```

### Step 4: Initialize Database

In a new terminal:

```bash
# Run database migrations (creates all tables)
docker compose -f docker-compose.local.yml exec backend alembic upgrade head
```

**Expected output:**
```
✅ INFO  [alembic.runtime.migration] Running upgrade  -> e2746ef4e845, initial_schema
```

### Step 5: Access Your Application

🎉 **You're ready!** Open these URLs:

- 🌐 **Frontend**: http://localhost:3000
- 🔧 **API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs (interactive Swagger UI)

**First-time login:**
1. Click "Login" button
2. Authenticate with your provider (Supabase/Auth0/Clerk)
3. You'll be redirected back to the app
4. Start uploading Twitter bookmarks!

---

## ✅ Verify Everything Works

Test the health endpoint:

```bash
curl http://localhost:8000/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

If you see this, congratulations! 🎉 Your POST BOT is running.

---

## 🛑 Stop the Application

```bash
docker compose -f docker-compose.local.yml down
```

To also remove volumes (database data):
```bash
docker compose -f docker-compose.local.yml down -v
```

---

## ☁️ Production Deployment

POST BOT uses a **simple single-VM deployment** with Docker Compose - no Kubernetes complexity needed.

### One-Time VM Setup

**Prerequisites:**
- Ubuntu 22.04+ VM (AWS EC2, DigitalOcean, etc.)
- Domain pointing to your VM's IP
- Ports 80/443 open

**1. Install Docker on your VM:**

```bash
# SSH into your VM
ssh ubuntu@your-vm-ip

# Run the bootstrap script
curl -fsSL https://raw.githubusercontent.com/your-username/postbot/main/scripts/ec2_bootstrap.sh | bash
```

This script installs:
- Docker & Docker Compose
- Nginx reverse proxy (optional but recommended)
- Configures SSL via Let's Encrypt

**2. Configure Nginx (optional but recommended):**

The script creates nginx config at `/etc/nginx/sites-available/postbot`. Edit if needed:

```bash
sudo nano /etc/nginx/sites-available/postbot
```

**Important:** The nginx config strips `/api` prefix:
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000/;  # Note the trailing slash!
}
```

This means:
- Client calls: `https://your-domain.com/api/profiles`
- Nginx forwards: `http://backend:8000/profiles` (without `/api`)
- **Your FastAPI routers should NOT have `/api` prefix** ✅ (already configured correctly)

### Automated Deployment with GitHub Actions

**1. Set up GitHub Secrets:**

Go to your GitHub repo → Settings → Secrets → Actions, add:

**VM Access:**
```
DEPLOY_HOST=your-vm-ip-or-domain
DEPLOY_USER=ubuntu
DEPLOY_PORT=22
DEPLOY_SSH_KEY=<your-private-ssh-key>
DEPLOY_PATH=/home/ubuntu/postbot
```

**Backend Environment:**
```
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_KEY=...
GROQ_API_KEY=gsk_...
```

**Frontend Build Variables:**
```
VITE_SUPABASE_URL=https://...
VITE_SUPABASE_ANON_KEY=...
VITE_API_URL=https://your-domain.com/api
VITE_REDIRECT_URL=https://your-domain.com
```

**GitHub Container Registry (optional):**
```
GHCR_USERNAME=your-github-username
GHCR_PAT=<your-github-personal-access-token>
```

**2. Deploy:**

```bash
# Automatic: Push to main branch
git push origin main

# Manual: Run workflow from GitHub Actions tab
# Actions → Deploy → Run workflow
```

**What happens during deployment:**
1. ✅ Builds Docker images for frontend & backend
2. ✅ Pushes images to GitHub Container Registry
3. ✅ SSHs to your VM
4. ✅ Pulls latest images
5. ✅ Recreates `.env` from GitHub Secrets
6. ✅ Runs `docker compose up -d`
7. ✅ Runs database migrations
8. ✅ Performs health check

**Deployment logs:**

```bash
# On your VM, check deployment
ssh ubuntu@your-vm-ip
cd /home/ubuntu/postbot
docker compose ps
docker logs postbot-backend -f
```

### Manual Deployment (for testing branches)

```bash
# On your VM
cd /home/ubuntu/postbot
git pull origin your-branch
docker compose pull
docker compose up -d --build
docker compose exec backend alembic upgrade head
```

### Post-Deployment Verification

```bash
# Check services are running
curl https://your-domain.com/api/health

# Expected response:
# {"status":"healthy","database":"connected","version":"1.0.0"}
```

For detailed deployment docs, see [docs/ec2.md](docs/ec2.md).

---

- One-time EC2 setup (Docker install + optional Nginx): [docs/ec2.md](docs/ec2.md)
- Ongoing deploy automation:
    - CI runs on PRs and pushes to `main`/`develop`.
    - Deploy builds & pushes images to GHCR, then the VM runs `docker compose pull` + `docker compose up -d`.

### What’s “one-time” vs “every deploy”

- **One-time on the VM:** Docker install + (optional) Nginx reverse proxy.
    - Script: `scripts/ec2_bootstrap.sh`
    - Nginx template you can edit: `scripts/nginx/postbot.conf.template`
- **Every deploy:** pull latest code + rebuild containers + run migrations.
- **Every deploy:** pull latest images + restart containers + run migrations.
    - Automated by GitHub Actions: `.github/workflows/deploy.yml`

### GitHub Actions secrets (for automated deploy)

Required repo secrets:
- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_PORT`
- `DEPLOY_SSH_KEY`
- `DEPLOY_PATH`

Required repo secrets for the backend:
- `DATABASE_URL` (Supabase Postgres connection string)

Required repo secrets for building the frontend image:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `API_URL`
- `REDIRECT_URL`

Security note: all `VITE_*` values are baked into the frontend bundle and are effectively public. `SUPABASE_KEY` here must be the Supabase **anon** key (never a service-role key).

Note: GHCR packages can be private by default even for public repos.
For the simplest setup, set the `postbot-frontend` and `postbot-backend` packages to **public** so the VM can pull without `docker login`.

If you keep GHCR packages private, add these optional secrets so the deploy job can `docker login` on the VM:
- `GHCR_USERNAME`
- `GHCR_PAT`

The deploy workflow recreates `DEPLOY_PATH/.env` on every deploy from GitHub Secrets.

Manual deploy for PR/branch testing:
- Actions → “Deploy” → Run workflow
- Defaults to deploying the selected ref’s current commit SHA (temporary testing)
- Optionally set `deploy_ref` to a branch/tag/SHA
- Optionally set `deploy_path` if you deploy PR builds to a separate folder/VM

## 🎬 Demo

**Live Demo:** [https://postbot-demo.example.com](https://postbot-demo.example.com) _(coming soon)_

### How it Works

![Postbot demo](assets/demo.gif)

**Step-by-step:**

1. **📥 Import Bookmarks**
   - Export your Twitter bookmarks as JSON
   - Upload to POST BOT
   - AI extracts all embedded content (links, PDFs, GitHub repos)

2. **🎯 Select & Configure**
   - Choose one or more tweets
   - Pick your writing style (Technical, Professional, Casual, Academic)
   - Customize tone, length, and target audience

3. **🤖 AI Generation**
   - LangGraph agent creates a structured outline
   - Writes each section with proper research
   - Generates title, intro, main body, and conclusion
   - Optionally creates social media posts (LinkedIn/Twitter)

4. **✏️ Review & Export**
   - Edit in built-in markdown editor
   - Export as Markdown, PDF, or DOCX
   - Publish directly or copy to your CMS

**What makes it special:**
- 🧠 **Intelligent Planning**: Agent creates outline before writing
- 🔗 **Deep Research**: Analyzes all linked content automatically
- 🎨 **Style Consistency**: Maintains your chosen tone throughout
- ⚡ **Fast**: Generates 2000+ word articles in under 60 seconds

---

This is the simplest way to run PostBot locally.

**Prereqs:** Docker + Docker Compose.

### 0. Create a local `.env`

```bash
cp .env.example .env
```

Minimum required values in `.env`:
- `DATABASE_URL`
- `SUPABASE_URL` + `SUPABASE_KEY` (default auth)
- `VITE_SUPABASE_URL` + `VITE_SUPABASE_ANON_KEY`
- `VITE_API_URL` + `VITE_REDIRECT_URL`
- At least one LLM key (example: `GROQ_API_KEY`)

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

High-level system view:

```
┌─────────────────────────────────────────────────────────────────┐
│                        User's Browser                            │
│                   (React 18 + TypeScript)                        │
└───────────────────────────┬─────────────────────────────────────┘
                │ HTTP(S)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                VM / EC2 (Docker Compose)                         │
│                                                                   │
│    ┌──────────────┐         ┌──────────────┐                     │
│    │   Frontend   │         │   Backend    │                     │
│    │ (Vite build) │◄────────┤   (FastAPI)  │                     │
│    └──────────────┘         └──────┬───────┘                     │
│                                     │                              │
└─────────────────────────────────────┼──────────────────────────────┘
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
| **Infrastructure** | Docker, Docker Compose |

### Key Features

- **Pluggable Authentication**: Switch between Supabase, Auth0, or Clerk
- **Multi-LLM Support**: Automatically falls back if primary LLM fails
- **Agentic Workflow**: LangGraph agents for intelligent content generation
- **Vector Search**: Semantic search using Qdrant embeddings
- **Production-Ready**: Health checks and repeatable deployments

---

## 🧠 Agent Architecture

Postbot’s generation pipeline is built as a **LangGraph state machine** that produces:

- A structured blog post (multi-section)
- Optional social posts (Twitter/X, LinkedIn)
- Optional tags

Agent architecture diagram:

![Postbot architecture diagram](assets/images/RiteUp%20Architecture.png)

### Core workflow (LangGraph)

Implementation: `src/backend/agents/blogs.py` (`AgentWorkflow`).

Key nodes:

1. **`generate_blog_plan`**
    - Creates a section outline from a template + user instructions.
2. **`write_section`** (map over main-body sections)
    - Writes each main-body section.
3. **`gather_completed_sections`**
    - Aggregates the completed main body into a single context block.
4. **`write_final_sections`** (map over non-main-body sections)
    - Writes intro/conclusion using the completed main-body context.
5. **`compile_final_blog`**
    - Concatenates sections and extracts a title.
6. **Optional post generation**
    - **`write_linkedin_post`** and/or **`write_twitter_post`** based on requested `post_types`.
7. **Feedback loop**
    - **`handle_feedback`** can route back to continue generating posts after feedback.

### State model

The graph carries a typed state object from `src/backend/agents/state.py`:

- `BlogState` (internal state)
- `BlogStateInput` (what the API provides)
- `BlogStateOutput` (what the API returns)

Important state fields:

- `sections` / `completed_sections` / `final_blog`
- `post_types` → drives whether LinkedIn/Twitter posts are generated
- `feedback` → triggers feedback routing
- `thread_id` → used for checkpointing/resume

### Checkpointing + resume

The workflow uses **LangGraph Postgres checkpointing** (`PostgresSaver`) so a run can be resumed/continued:

- Checkpointer: `langgraph.checkpoint.postgres.PostgresSaver`
- Storage: PostgreSQL (your `DATABASE_URL`)
- Tables: created via Alembic migration (checkpoint tables)

### Reference enrichment

Before/while generating, Postbot can enrich context via:

- URL extraction / conversion (`src/backend/extraction/…`)
- Web search (`WebSearch`)
- Image search (`ImageSearch`)
- Reddit search (`RedditSearch`)

These tools live in `src/backend/agents/tools.py` and are enabled only if you set the corresponding API keys.

### Templates + style control

The blog generation prompt is driven by templates and parameters:

- Prompts: `src/backend/agents/prompts.py`
- Default template parameters live in `AgentWorkflow.DEFAULT_TEMPLATE_PARAMS`
- You can provide a template payload (`template`) that overrides persona/tone/length/etc.

---

## ⚙️ Configuration

### Complete Environment Variables Reference

<details>
<summary><b>🔴 Required: Database & Core</b></summary>

```env
# ============================================
# Database Connection (REQUIRED)
# ============================================
# For Supabase: Use Transaction pooler (port 5432)
DATABASE_URL=postgresql://postgres.[PROJECT]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres?sslmode=require

# For other PostgreSQL providers:
# DATABASE_URL=postgresql://user:password@host:5432/database

# ============================================
# Application URLs (REQUIRED)
# ============================================
# Backend API URL (for internal communication)
API_URL=http://localhost:8000

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000

# Allowed CORS origins (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# ============================================
# Environment & Logging
# ============================================
ENVIRONMENT=development  # or production
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
```

**Getting Supabase DATABASE_URL:**
1. Go to your Supabase project → Settings → Database
2. Click "Connection string" → "Transaction" mode
3. Copy the string, replace `[YOUR-PASSWORD]` with your actual password
4. Add `?sslmode=require` at the end

</details>

<details>
<summary><b>🔴 Required: Authentication (Choose One Provider)</b></summary>

**Option 1: Supabase (Recommended)**
```env
AUTH_PROVIDER=supabase

# Backend needs these
SUPABASE_URL=https://[PROJECT].supabase.co
SUPABASE_KEY=eyJhbG...                      # Service role key

# Frontend needs these (different keys!)
VITE_SUPABASE_URL=https://[PROJECT].supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbG...            # Anon public key (NOT service role!)
```

**Getting Supabase keys:**
1. Supabase project → Settings → API
2. **Project URL**: Copy to `SUPABASE_URL` and `VITE_SUPABASE_URL`
3. **anon public** key: Copy to `VITE_SUPABASE_ANON_KEY`
4. **service_role** key: Copy to `SUPABASE_KEY` (⚠️ Keep this secret!)

**Option 2: Auth0**
```env
AUTH_PROVIDER=auth0

# Backend
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-secret

# Frontend
VITE_AUTH0_DOMAIN=your-tenant.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
```

**Option 3: Clerk**
```env
AUTH_PROVIDER=clerk

# Backend
CLERK_SECRET_KEY=sk_test_xxx

# Frontend
VITE_CLERK_PUBLISHABLE_KEY=pk_test_xxx
```

</details>

<details>
<summary><b>🔴 Required: Frontend URLs</b></summary>

```env
# ============================================
# Frontend Build-Time Variables (REQUIRED)
# ============================================
# These are BAKED INTO the frontend bundle

# API endpoint the frontend will call
VITE_API_URL=http://localhost:8000           # Local
# VITE_API_URL=https://api.yourdomain.com    # Production

# Where to redirect after login
VITE_REDIRECT_URL=http://localhost:3000      # Local
# VITE_REDIRECT_URL=https://yourdomain.com   # Production
```

**⚠️ Important:** All `VITE_*` variables are:
- Embedded in the frontend JavaScript bundle
- **Publicly visible** in the browser
- Must be set **before building** the frontend
- Never put secrets in `VITE_*` variables!

</details>

<details>
<summary><b>🔴 Required: LLM API Keys (At Least One)</b></summary>

```env
# ============================================
# LLM Provider Keys (At least ONE required)
# ============================================

# Groq (Recommended - fast & generous free tier)
GROQ_API_KEY=gsk_...
# Get key: https://console.groq.com/keys

# Google Gemini (Free tier available)
GEMINI_API_KEY=AIza...
# Get key: https://makersuite.google.com/app/apikey

# OpenRouter (Access to multiple models)
OPENROUTER_API_KEY=sk-or-...
# Get key: https://openrouter.ai/keys

# DeepSeek
DEEPSEEK_API_KEY=sk-...
# Get key: https://platform.deepseek.com/api_keys

# Ollama (Local models)
OLLAMA_API_KEY=ollama
OLLAMA_BASE_URL=http://localhost:11434
# Install: https://ollama.ai
```

**Fallback behavior:** If primary LLM fails, POST BOT automatically tries the next available provider.

</details>

<details>
<summary><b>🟡 Optional: Search & Image Services</b></summary>

```env
# ============================================
# Optional: Enhanced Features
# ============================================

# Web Search (for content enrichment)
SERPER_API_KEY=your-key
# Get key: https://serper.dev (100 free searches/day)

# Image Search (for blog illustrations)
PIXABAY_API_KEY=your-key
# Get key: https://pixabay.com/api/docs/ (free)

# Reddit API (for Reddit content extraction)
REDDIT_CLIENT_ID=your-id
REDDIT_CLIENT_SECRET=your-secret
REDDIT_USER_AGENT=postbot:v1.0.0
# Create app: https://www.reddit.com/prefs/apps
```

**Note:** These are optional. POST BOT works without them, but content enrichment features won't be available.

</details>

<details>
<summary><b>🟢 Optional: Advanced Configuration</b></summary>

```env
# ============================================
# Performance & Caching
# ============================================
AUTH_CACHE_SIZE=1000          # Token cache size
AUTH_CACHE_TTL=300            # Token cache TTL (seconds)

# ============================================
# Rate Limiting
# ============================================
RATE_LIMIT_PER_MINUTE=60      # API requests per minute
RATE_LIMIT_PER_HOUR=1000      # API requests per hour

# ============================================
# LangGraph Checkpointing
# ============================================
# Uses PostgreSQL (same as DATABASE_URL)
# No additional config needed - uses checkpoint tables from migration

# ============================================
# Vector Database (Qdrant)
# ============================================
# Coming soon - semantic search features
# QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=your-key
```

</details>

### Configuration Checklist

Before running POST BOT, ensure you have:

- ✅ `DATABASE_URL` - PostgreSQL connection string
- ✅ `AUTH_PROVIDER` + auth keys - Supabase/Auth0/Clerk credentials  
- ✅ `VITE_SUPABASE_URL` + `VITE_SUPABASE_ANON_KEY` - Frontend auth
- ✅ `VITE_API_URL` + `VITE_REDIRECT_URL` - Frontend URLs
- ✅ At least ONE LLM API key - Groq, Gemini, OpenRouter, etc.
- ✅ `ALLOWED_ORIGINS` - CORS whitelist

**Quick validation:**

```bash
# Check all required vars are set
docker compose -f docker-compose.local.yml config | grep -E "DATABASE_URL|SUPABASE|GROQ|VITE_"
```

---

### Database Migrations

POST BOT uses Alembic for database schema management.

**Initial setup (already done if you followed Quick Start):**

```bash
# Run all migrations
docker compose -f docker-compose.local.yml exec backend alembic upgrade head
```

**Common commands:**

```bash
# Check current version
docker compose -f docker-compose.local.yml exec backend alembic current

# View migration history
docker compose -f docker-compose.local.yml exec backend alembic history

# Rollback one version
docker compose -f docker-compose.local.yml exec backend alembic downgrade -1

# Create new migration (after model changes)
docker compose -f docker-compose.local.yml exec backend alembic revision --autogenerate -m "add new feature"
```

**What gets created:**
- ✅ **31 application tables**: profiles, content, sources, templates, etc.
- ✅ **4 LangGraph checkpoint tables**: for AI agent state persistence
- ✅ **Reference data**: content types (blog, article), source types (twitter, reddit), default parameters

**Production deployment:** Migrations run automatically during GitHub Actions deploy.

**Troubleshooting:**

If migrations fail with "relation already exists" (tables were created manually):

```bash
# Stamp database without creating tables
docker compose -f docker-compose.local.yml exec backend alembic stamp head
```

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

### Local Development (Without Docker)

For faster iteration during development, you can run services directly:

**Prerequisites:**
- Python 3.12+
- Node.js 18+
- PostgreSQL 14+ (local or remote)

**Backend Setup:**

```bash
# Navigate to backend
cd src/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt -r requirements_llm.txt

# Set up environment
cp ../../.env.example ../../.env
# Edit .env with your values

# Run migrations
alembic upgrade head

# Start development server (auto-reload on code changes)
uvicorn api.api:app --reload --port 8000
```

**Frontend Setup:**

```bash
# Navigate to frontend
cd src/frontend/project

# Install dependencies
npm install

# Start development server (Vite hot reload)
npm run dev
```

**Access:**
- Frontend: http://localhost:5173 (Vite default port)
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Hot Reload:**
- Backend: Uvicorn auto-reloads on Python file changes
- Frontend: Vite hot-reloads on React/TypeScript changes

### Development with Docker (Recommended for consistency)

Use Docker Compose for a production-like environment:

```bash
# Start all services
docker compose -f docker-compose.local.yml up --build

# Run specific service
docker compose -f docker-compose.local.yml up backend

# View logs
docker compose -f docker-compose.local.yml logs -f backend

# Execute commands in running container
docker compose -f docker-compose.local.yml exec backend bash
docker compose -f docker-compose.local.yml exec backend alembic current

# Rebuild after dependency changes
docker compose -f docker-compose.local.yml build --no-cache
```

### Project Structure

```
postbot/
├── .github/
│   └── workflows/
│       ├── ci.yml           # Test & lint on PRs
│       └── deploy.yml       # Production deployment
├── alembic/
│   ├── versions/            # Database migrations
│   └── env.py              # Alembic configuration
├── scripts/
│   ├── ec2_bootstrap.sh    # VM initial setup
│   └── nginx/              # Nginx config templates
├── src/
│   ├── backend/
│   │   ├── agents/         # 🤖 LangGraph AI agents
│   │   │   ├── blogs.py    # Main blog generation workflow
│   │   │   ├── state.py    # State management
│   │   │   ├── tools.py    # Search & extraction tools
│   │   │   └── prompts/    # AI prompt templates
│   │   ├── api/
│   │   │   ├── api.py      # FastAPI app & middleware
│   │   │   ├── routers/    # API endpoints
│   │   │   └── dependencies.py  # Auth & DB dependencies
│   │   ├── auth/           # 🔐 Authentication providers
│   │   │   ├── factory.py  # Provider factory (Supabase/Auth0/Clerk)
│   │   │   └── providers/  # Provider implementations
│   │   ├── db/
│   │   │   ├── models.py   # SQLAlchemy models
│   │   │   ├── repositories/  # Data access layer
│   │   │   └── connection.py  # Database connection
│   │   ├── extraction/     # 📄 Content extractors
│   │   │   ├── github.py   # GitHub repo analysis
│   │   │   ├── pdf.py      # PDF extraction
│   │   │   └── html.py     # Web page scraping
│   │   └── utils/          # Logging, config, helpers
│   └── frontend/
│       └── project/
│           ├── src/
│           │   ├── components/  # React components
│           │   ├── services/    # API client
│           │   ├── pages/       # Route components
│           │   └── context/     # Auth & state
│           ├── public/          # Static assets
│           └── vite.config.ts   # Vite configuration
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── Dockerfile.backend      # Backend container
├── Dockerfile.frontend     # Frontend container  
├── docker-compose.yml      # Production compose
├── docker-compose.local.yml  # Local development compose
├── Makefile               # Development shortcuts
└── .env.example           # Environment template
```

### Key Files Explained

| File | Purpose |
|------|---------|
| `src/backend/agents/blogs.py` | Main LangGraph workflow for blog generation |
| `src/backend/api/api.py` | FastAPI application setup, middleware, CORS |
| `src/backend/api/routers/` | API endpoints (profiles, content, sources, etc.) |
| `src/backend/auth/factory.py` | Authentication provider factory pattern |
| `src/backend/db/models.py` | Database schema (31 tables) |
| `alembic/versions/e2746ef4e845_initial_schema.py` | Initial database migration |
| `.github/workflows/deploy.yml` | CI/CD deployment automation |
| `docker-compose.local.yml` | Local development environment |

### Useful Development Commands

```bash
# ============================================
# Database
# ============================================
# Create new migration after model changes
docker compose -f docker-compose.local.yml exec backend \
  alembic revision --autogenerate -m "add new feature"

# Apply migrations
docker compose -f docker-compose.local.yml exec backend alembic upgrade head

# Rollback migration
docker compose -f docker-compose.local.yml exec backend alembic downgrade -1

# View migration history
docker compose -f docker-compose.local.yml exec backend alembic history

# ============================================
# Testing
# ============================================
# Run all tests
docker compose -f docker-compose.local.yml exec backend pytest

# Run specific test file
docker compose -f docker-compose.local.yml exec backend pytest tests/unit/test_agents.py

# Run with coverage
docker compose -f docker-compose.local.yml exec backend pytest --cov=src

# ============================================
# Code Quality
# ============================================
# Format code
docker compose -f docker-compose.local.yml exec backend black src/

# Lint
docker compose -f docker-compose.local.yml exec backend ruff check src/

# Type checking
docker compose -f docker-compose.local.yml exec backend mypy src/

# ============================================
# Cleanup
# ============================================
# Stop all services
docker compose -f docker-compose.local.yml down

# Remove volumes (⚠️ deletes data)
docker compose -f docker-compose.local.yml down -v

# Remove images
docker compose -f docker-compose.local.yml down --rmi all

# Full cleanup
docker system prune -a --volumes
```

### Making Changes

**1. Create a branch:**
```bash
git checkout -b feature/your-feature-name
```

**2. Make changes and test:**
```bash
# Start services
docker compose -f docker-compose.local.yml up -d

# Watch logs
docker compose -f docker-compose.local.yml logs -f

# Run tests
docker compose -f docker-compose.local.yml exec backend pytest
```

**3. Commit with clear messages:**
```bash
git add .
git commit -m "feat: add new feature"  # Use conventional commits
git push origin feature/your-feature-name
```

**Commit message prefixes:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance

**4. Open Pull Request:**
- Go to GitHub repository
- Click "Pull Request"
- Fill in description (what, why, how)
- Wait for CI checks to pass

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
cp .env.example .env
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

### Common Issues & Solutions

<details>
<summary><b>❌ "Cannot connect to server" in frontend</b></summary>

**Symptoms:** Frontend shows connection error, network tab shows failed API calls.

**Solution:**

1. Check backend is running:
   ```bash
   docker compose -f docker-compose.local.yml ps
   # Should show "backend" as "Up"
   ```

2. Check backend logs:
   ```bash
   docker logs postbot-backend-local --tail 50
   # Look for "Uvicorn running on http://0.0.0.0:8000"
   ```

3. Verify `VITE_API_URL` in `.env`:
   ```bash
   # For local development
   VITE_API_URL=http://localhost:8000
   
   # For production
   VITE_API_URL=https://your-domain.com/api
   ```

4. Check CORS settings:
   ```bash
   # In .env, ensure ALLOWED_ORIGINS includes your frontend URL
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
   ```

</details>

<details>
<summary><b>❌ Database connection failed</b></summary>

**Symptoms:** Backend logs show `could not connect to server` or `FATAL: password authentication failed`.

**Solution:**

1. Test database connection:
   ```bash
   # Copy your DATABASE_URL from .env
   psql "postgresql://..."
   ```

2. Common issues:
   - **Wrong port**: Use `5432` for direct connection, `6543` for Supabase pooler
   - **SSL required**: Supabase requires `?sslmode=require` at end of connection string
   - **IP allowlist**: Check Supabase dashboard → Database → Connection Pooling → Add your IP

3. Correct Supabase format:
   ```bash
   # Use Transaction mode pooler (port 5432)
   DATABASE_URL=postgresql://postgres.[PROJECT]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres?sslmode=require
   ```

</details>

<details>
<summary><b>❌ 404 on /api/profiles endpoint</b></summary>

**Symptoms:** API calls return 404 even though route exists.

**Cause:** Nginx configuration strips `/api` prefix before forwarding to backend.

**Solution:** ✅ Already fixed! FastAPI routers should NOT have `/api` prefix since nginx strips it. Verify:

```python
# ✅ Correct (in api.py)
app.include_router(profiles.router)  # No prefix!

# ❌ Wrong
app.include_router(profiles.router, prefix="/api")
```

If you see 404s after deployment, ensure:
1. Latest code is deployed
2. Backend container restarted: `docker compose restart backend`
3. Nginx config has trailing slash: `proxy_pass http://127.0.0.1:8000/;`

</details>

<details>
<summary><b>❌ Authentication not working</b></summary>

**Symptoms:** Login button does nothing, or redirects to error page.

**Solution:**

1. Check auth provider is configured:
   ```bash
   docker exec postbot-backend-local env | grep AUTH
   # Should show AUTH_PROVIDER=supabase and related keys
   ```

2. Verify redirect URLs in auth provider dashboard:
   - **Supabase**: Authentication → URL Configuration
   - Add: `http://localhost:3000` (local)
   - Add: `https://your-domain.com` (production)

3. Check browser console for errors (F12 → Console tab)

4. Verify frontend env vars:
   ```bash
   # In .env
   VITE_SUPABASE_URL=https://[PROJECT].supabase.co
   VITE_SUPABASE_ANON_KEY=eyJ...  # Must be anon key, not service role!
   VITE_REDIRECT_URL=http://localhost:3000  # Must match your frontend URL
   ```

</details>

<details>
<summary><b>❌ LLM generation fails</b></summary>

**Symptoms:** "Content generation failed" error, or infinite loading.

**Solution:**

1. Verify API key is set:
   ```bash
   docker exec postbot-backend-local env | grep API_KEY
   ```

2. Test API key manually:
   ```bash
   # For Groq
   curl -H "Authorization: Bearer $GROQ_API_KEY" \
        https://api.groq.com/openai/v1/models
   ```

3. Check backend logs for specific error:
   ```bash
   docker logs postbot-backend-local --tail 100 | grep -i error
   ```

4. Common issues:
   - **Rate limit exceeded**: Wait a few minutes or switch to different LLM
   - **Invalid API key**: Regenerate key in provider dashboard
   - **No quota remaining**: Check billing in provider dashboard

</details>

<details>
<summary><b>❌ Migrations fail with "relation already exists"</b></summary>

**Symptoms:** `alembic upgrade head` fails with duplicate table errors.

**Cause:** Tables were created manually before running migrations.

**Solution:**

```bash
# Stamp database to current migration without creating tables
docker compose -f docker-compose.local.yml exec backend alembic stamp head

# Verify
docker compose -f docker-compose.local.yml exec backend alembic current
# Should show: e2746ef4e845 (head)
```

For production database that was manually created, the deploy script handles this automatically.

</details>

<details>
<summary><b>❌ Docker image build fails with "invalid reference format"</b></summary>

**Cause:** Missing `POSTBOT_IMAGE_OWNER` environment variable.

**Solution:**

```bash
# Set in your .env or export it
export POSTBOT_IMAGE_OWNER=your-github-username

# Or for local testing, use docker-compose.local.yml which doesn't need it
docker compose -f docker-compose.local.yml up --build
```

</details>

<details>
<summary><b>❌ Frontend build fails with "process is not defined"</b></summary>

**Cause:** Missing environment variables during build.

**Solution:**

```bash
# Ensure all VITE_* variables are in .env
grep VITE_ .env

# Should show:
# VITE_SUPABASE_URL=...
# VITE_SUPABASE_ANON_KEY=...
# VITE_API_URL=...
# VITE_REDIRECT_URL=...

# Rebuild
docker compose -f docker-compose.local.yml up --build frontend
```

</details>

### Still Having Issues?

1. **Check all logs:**
   ```bash
   # Backend
   docker logs postbot-backend-local --tail 200
   
   # Frontend
   docker logs postbot-frontend-local --tail 200
   
   # Both
   docker compose -f docker-compose.local.yml logs -f
   ```

2. **Verify environment variables:**
   ```bash
   # Check what's loaded
   docker exec postbot-backend-local env | sort
   ```

3. **Fresh start:**
   ```bash
   # Stop and remove everything
   docker compose -f docker-compose.local.yml down -v
   
   # Rebuild from scratch
   docker compose -f docker-compose.local.yml up --build
   ```

4. **Get help:**
   - 🐛 [Open an Issue](https://github.com/your-username/postbot/issues) with:
     - Steps to reproduce
     - Full error messages
     - Docker logs
     - Your environment (OS, Docker version)
   - 💬 [GitHub Discussions](https://github.com/your-username/postbot/discussions)

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
- **Infrastructure**: [Docker](https://www.docker.com/)

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