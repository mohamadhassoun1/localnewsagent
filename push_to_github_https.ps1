<#
Push LocalNewsAgent to GitHub using HTTPS + Personal Access Token (PAT).
No GitHub CLI required.

Usage:
  .\push_to_github_https.ps1 -RepoName "localnewsagent" -UserName "your-github-username" -Token "your-pat-token"

To create a PAT:
  1. Go to https://github.com/settings/tokens
  2. Click "Generate new token (classic)"
  3. Select scopes: repo, workflow
  4. Copy the token and pass it here
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$RepoName,

    [Parameter(Mandatory=$true)]
    [string]$UserName,

    [Parameter(Mandatory=$true)]
    [string]$Token
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $root

if (-not (Test-Path '.git')) {
    Write-Error "Git repository not initialized. Run 'git init' first."
    Pop-Location
    exit 1
}

$repoUrl = "https://${UserName}:${Token}@github.com/${UserName}/${RepoName}.git"

Write-Host "Pushing to GitHub..."
Write-Host "Repository: https://github.com/$UserName/$RepoName"

# Add remote and push
git remote add origin $repoUrl 2>$null
git branch -M main
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Repository pushed successfully!"
    Write-Host ""
    Write-Host "GitHub repo:" "https://github.com/$UserName/$RepoName"
    Write-Host "Actions:" "https://github.com/$UserName/$RepoName/actions"
    Write-Host ""
    Write-Host "The GitHub Actions workflow will now build a Docker image and push it to GitHub Container Registry (GHCR)."
    Write-Host "Container image: ghcr.io/$UserName/$RepoName:latest"
    Write-Host ""
    Write-Host "Next: Deploy the container to a hosting service (Render, Fly.io, Railway, etc.)"
} else {
    Write-Error "Push failed. Check your credentials and try again."
    Pop-Location
    exit 1
}

Pop-Location
