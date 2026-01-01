<div align="center">

# 🚀 POST BOT

### Transform Your Tweets into Engaging Blog Content with AI

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg?logo=react)](https://reactjs.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**[Deploy](#-deploy-ec2--vm)** • **[Demo](#-demo)** • **[Quick Start](#-quick-start-10-minutes)** • **[Features](#-features)** • **[Architecture](#-architecture)** • **[Agent Architecture](#-agent-architecture)** • **[Contributing](#-contributing)**

</div>

## 🚀 Deploy (EC2 / VM)

Production deployment is intentionally simple: **one VM + Docker Compose**.

- One-time EC2 setup (Docker install + optional Nginx): [docs/ec2.md](docs/ec2.md)
- Ongoing deploy automation:
    - A single GitHub Actions pipeline runs **Build → Test → Deploy**.
    - Deploy runs only on pushes to `main` (or manual dispatch) and updates the VM with `docker compose up -d --build`.

### What’s “one-time” vs “every deploy”

- **One-time on the VM:** Docker install + (optional) Nginx reverse proxy.
    - Script: `scripts/ec2_bootstrap.sh`
    - Nginx template you can edit: `scripts/nginx/postbot.conf.template`
- **Every deploy:** pull latest code + rebuild containers + run migrations.
    - Automated by GitHub Actions: `.github/workflows/ci.yml`

### GitHub Actions secrets (for automated deploy)

Required repo secrets:
- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_PORT`
- `DEPLOY_SSH_KEY`
- `DEPLOY_PATH`

The VM must also have a `.env` file at `DEPLOY_PATH/.env` (it is not stored in GitHub secrets).

Manual deploy for PR/branch testing:
- Actions → “Build, Test, Deploy” → Run workflow
- Defaults to deploying the selected ref’s current commit SHA (temporary testing)
- Optionally set `deploy_ref` to a branch/tag/SHA
- Optionally set `deploy_path` if you deploy PR builds to a separate folder/VM

## 🎬 Demo

Demo GIF:

![Postbot demo](assets/demo.gif)

UI screenshot:

![Postbot UX](assets/images/UX.png)

## ⚡ Quick Start (10 minutes)

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

![Postbot architecture diagram](assets/images/RiteUp%20Architecture.png)

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

### Manual Run (without Docker)

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
└── .env.example              # Environment template
```

### Useful Commands

```bash
# Local (Docker Compose)
docker compose -f docker-compose.local.yml up --build
docker compose -f docker-compose.local.yml logs -f
docker compose -f docker-compose.local.yml down

\

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

# If this is a fresh deploy, run migrations:
# docker compose run --rm backend alembic upgrade head
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