# Deploying LocalNewsAgent

This document explains how to push the project to GitHub and deploy it to a container host.

Prerequisites (local):
- Git (https://git-scm.com)
- GitHub CLI (`gh`) authenticated (https://cli.github.com)
- Docker (for local testing)

Quick steps to push repository and enable CI build:

1. Create remote repo & push (PowerShell):

```powershell
.\push_to_github.ps1 -RepoName "your-username/localnewsagent" -Private:$false
```

This uses the GitHub CLI to create a remote repo and push the code.

2. (Optional) Configure Render deployment

- Create a Render Web Service and note the `service id` (srv-...)
- In your GitHub repository, add two secrets:
  - `RENDER_API_KEY` — your Render API key
  - `RENDER_SERVICE_ID` — the service id (without the `srv-` prefix may vary)

You can add them using `gh`:

```powershell
gh secret set RENDER_API_KEY --body "<your-key>"
gh secret set RENDER_SERVICE_ID --body "<service-id>"
```

3. The GitHub Actions workflow `.github/workflows/ci-deploy.yml` builds and pushes a Docker image to `ghcr.io/<owner>/<repo>:latest`. If `RENDER_API_KEY` and `RENDER_SERVICE_ID` are set it will also trigger a manual deploy on Render.

Local testing

```powershell
# Build and run locally with Docker Compose
docker compose up --build

# Or run directly
python publish.py
python server.py
```

Security note

The `/publish` endpoint is intentionally convenient for local demos and runs `publish.py`. Do not expose this server publicly without securing that endpoint (remove or protect it with authentication).
