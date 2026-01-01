# Deploy to EC2 (Docker Compose)

This repo intentionally keeps deployment **boring**:
- One EC2 instance
- `docker compose up -d`
- A single `.env` file on the server

## One-time EC2 setup

### 1) Launch the instance
- Ubuntu 22.04/24.04 is fine.
- Security Group:
  - Allow SSH (22) from your IP.
  - For a simple direct setup, allow:
    - 3000 (frontend) and 8000 (backend) from your IP, OR
    - 80/443 if you put a reverse proxy in front (optional; not covered here).

### 2) One-time install: Docker (+ optional Nginx)
This repo includes a small one-time bootstrap script:

- Installs Docker Engine + `docker compose` plugin
- Optionally installs/configures Nginx using a template you can edit

On the EC2 instance:
```bash
sudo bash scripts/ec2_bootstrap.sh --install-docker
```

Optional Nginx setup (reverse proxy to frontend/backend):

1) Copy the template and edit it (local machine or on the server):
```bash
cp scripts/nginx/postbot.conf.template /tmp/postbot.conf.template
```

2) Run the script pointing to your template:
```bash
sudo bash scripts/ec2_bootstrap.sh --setup-nginx \
  --domain postbot.example.com \
  --nginx-template /tmp/postbot.conf.template \
  --frontend-port 3000 \
  --backend-port 8000
```

You can also do this over SSH from your laptop:
```bash
scp scripts/nginx/postbot.conf.template ubuntu@<HOST>:/tmp/postbot.conf.template
ssh ubuntu@<HOST> "cd ~/postbot && sudo bash scripts/ec2_bootstrap.sh --install-docker --setup-nginx --domain postbot.example.com --nginx-template /tmp/postbot.conf.template"
```

### 3) Create a deploy directory
Pick a simple location (example uses your home directory):
```bash
mkdir -p ~/postbot
cd ~/postbot
```

### 4) Create the server `.env`
On the EC2 instance (in the deploy directory):
```bash
touch .env
nano .env
```

Tip: easiest is to create it locally and upload it once:
```bash
cp .env.example .env

# edit .env locally, then upload it
scp -i <path-to-key> .env <user>@<host>:~/postbot/.env
```

Required values:
- `DATABASE_URL`
- `SUPABASE_URL` + `SUPABASE_KEY` (when `AUTH_PROVIDER=supabase`)
- `VITE_SUPABASE_URL` + `VITE_SUPABASE_ANON_KEY`
- `VITE_API_URL` + `VITE_REDIRECT_URL`
- At least one LLM key (e.g. `GROQ_API_KEY`)

## Deploy / update

Deploy can be automated from GitHub Actions via [deploy workflow](../.github/workflows/deploy.yml).

This repo uses a registry-based deploy:
- GitHub Actions builds & pushes images to GHCR
- The VM pulls the images and runs `docker compose` (no repo clone required)

For PR/branch testing: run the workflow manually (Actions → “Deploy” → Run workflow) and set:
- by default it deploys the selected ref’s current commit SHA (temporary testing)
- optionally set `deploy_ref` to your branch name (or tag/SHA)
- optionally `deploy_path` if you deploy PR builds to a separate folder/VM

Prereqs for automated deploy:
- A deploy directory exists on the VM (example: `~/postbot`).
- A `.env` file exists on the VM in that directory.
- GitHub repo secrets are set:
  - `DEPLOY_HOST`
  - `DEPLOY_USER`
  - `DEPLOY_PORT`
  - `DEPLOY_SSH_KEY`
  - `DEPLOY_PATH`

Optional (only if GHCR packages are private):
- `GHCR_USERNAME`
- `GHCR_PAT`

If you want to deploy manually from the VM:
```bash
cd ~/postbot

docker compose pull

docker compose up -d --remove-orphans

docker compose run --rm backend alembic upgrade head
```

## Logs / health
```bash
docker compose ps

docker compose logs -f --tail 200
```

## Stop
```bash
docker compose down
```
