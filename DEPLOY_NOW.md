# LocalNewsAgent - Deployment Instructions

Your project is ready to deploy! Follow these steps to go public.

## Step 1: Create a GitHub Personal Access Token (PAT)

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name: `localnewsagent-deploy`
4. Select scopes:
   - ☑ `repo` (full control of repositories)
   - ☑ `workflow` (update GitHub Action workflows)
5. Click "Generate token"
6. **Copy the token** (you'll only see it once)

## Step 2: Push to GitHub

Run this command (replace with your GitHub username and paste your token):

```powershell
cd 'C:\Users\moham\Desktop\blog'
.\push_to_github_https.ps1 -RepoName "localnewsagent" -UserName "YOUR_GITHUB_USERNAME" -Token "YOUR_PAT_TOKEN"
```

Example:
```powershell
.\push_to_github_https.ps1 -RepoName "localnewsagent" -UserName "john-doe" -Token "ghp_xxxxxxxxxxxxxxxxxxxx"
```

This will:
- Create a remote `origin` pointing to your GitHub repo
- Push all code to GitHub
- Print your repo URL and Actions URL

## Step 3: Watch the Build

GitHub Actions will automatically:
1. Build a Docker container
2. Push it to `ghcr.io/YOUR_USERNAME/localnewsagent:latest`

Monitor progress at: `https://github.com/YOUR_USERNAME/localnewsagent/actions`

## Step 4: Deploy to a Public Host

Choose one:

### Option A: Render (Easiest)
1. Go to https://render.com and sign up
2. Create a "New Web Service"
3. Select "Deploy an existing image"
4. Enter: `ghcr.io/YOUR_USERNAME/localnewsagent:latest`
5. Set port: `8080`
6. Click "Create Web Service"
7. Render will give you a public URL (e.g., `https://your-service.onrender.com`)

### Option B: Fly.io
1. Go to https://fly.io and sign up
2. Install `flyctl` (CLI)
3. Run from project root:
   ```bash
   flyctl launch
   flyctl deploy --image ghcr.io/YOUR_USERNAME/localnewsagent:latest
   ```
4. Fly will assign a public URL

### Option C: Railway
1. Go to https://railway.app and sign up
2. Create a new project → Deploy from GitHub
3. Select your `localnewsagent` repo
4. Railway auto-detects Docker and deploys
5. You get a public URL in the dashboard

## Security Note

The `/publish` endpoint is protected with a `PUBLISH_TOKEN` env var. 

On your hosting platform, set:
- Environment variable: `PUBLISH_TOKEN=your-secret-token-here`

Then call the publish endpoint with the token:
```
https://your-public-url.com/publish?token=your-secret-token-here
```

## Local Testing

Before deploying, test locally:

```powershell
# Run the server
python publish.py
python server.py

# Visit http://localhost:8080
```

---

**Questions?** Check `DEPLOYMENT.md` or `README.md` for more details.
