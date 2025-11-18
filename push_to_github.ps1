<#
PowerShell helper to create a GitHub repo (using gh) and push the current folder.

Requirements:
- Git installed and configured
- GitHub CLI (`gh`) installed and authenticated (`gh auth login`)

Usage:
  .\push_to_github.ps1 -RepoName "localnewsagent" -Private:$false
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$RepoName,

    [switch]$Private
)

$isPrivate = $Private.IsPresent

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI 'gh' not found. Install and authenticate before running this script."
    exit 1
}

if (-not (Test-Path .git)) {
    git init
}

git add --all
git commit -m "Initial commit: LocalNewsAgent"

Write-Host "Creating remote repository '$RepoName'..."
$args = @($RepoName)
if ($isPrivate) { $args += '--private' }
gh repo create @args --source=. --remote=origin --push

Write-Host "Repository created and pushed. To set deployment secrets run:"
Write-Host "  gh secret set RENDER_API_KEY --body '<your-key>'"
Write-Host "  gh secret set RENDER_SERVICE_ID --body '<service-id>'"
