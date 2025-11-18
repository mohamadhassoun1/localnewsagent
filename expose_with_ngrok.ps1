<#
Expose LocalNewsAgent via ngrok and automate publish + server start.

Usage (no prompts):
  .\expose_with_ngrok.ps1 -PublishToken 'mytoken123' -NgrokPath 'C:\path\to\ngrok.exe'

If `NgrokPath` is not provided, the script expects `ngrok` to be on PATH.
If `PublishToken` is not provided, a GUID will be generated and used.

Prerequisites:
- Python and required packages installed
- ngrok installed and (optionally) authenticated
#>

param(
    [string]$PublishToken = $(New-Guid).Guid,
    [string]$NgrokPath = "ngrok"
)

Set-StrictMode -Version Latest

Write-Host "Using publish token:" $PublishToken

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $root

if (-not (Test-Path './publish.py')) {
    Write-Error "publish.py not found in $root. Run this script from project root."
    Pop-Location
    exit 1
}

Write-Host "Running publish.py to generate published files..."
python publish.py
if ($LASTEXITCODE -ne 0) {
    Write-Warning "publish.py exited with code $LASTEXITCODE"
}

Write-Host "Starting server.py in background (PUBLISH_TOKEN set for this session)..."
$env:PUBLISH_TOKEN = $PublishToken

# Start the server in a new hidden window
$serverProc = Start-Process -FilePath python -ArgumentList 'server.py' -WorkingDirectory $root -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 1

if (-not $serverProc) {
    Write-Error "Failed to start server.py"
    Pop-Location
    exit 1
}

Write-Host "Server started (PID: $($serverProc.Id)). Now starting ngrok..."

if (-not (Get-Command $NgrokPath -ErrorAction SilentlyContinue)) {
    Write-Warning "ngrok not found at '$NgrokPath' or not on PATH. Install ngrok from https://ngrok.com and ensure it's on PATH. Exiting."
    Write-Host "Server is running locally at http://localhost:8080"
    Pop-Location
    exit 0
}

# Start ngrok to expose port 8080. Use --log=stdout so the web inspector is available.
$ngrokProc = Start-Process -FilePath $NgrokPath -ArgumentList 'http', '8080', '--log=stdout' -WorkingDirectory $root -WindowStyle Hidden -PassThru

if (-not $ngrokProc) {
    Write-Error "Failed to start ngrok"
    Pop-Location
    exit 1
}

Write-Host "Waiting for ngrok to provide public URL (querying http://127.0.0.1:4040)..."

for ($i = 0; $i -lt 30; $i++) {
    try {
        $tunnels = Invoke-RestMethod -UseBasicParsing -Uri 'http://127.0.0.1:4040/api/tunnels' -ErrorAction Stop
        if ($tunnels.tunnels.Count -gt 0) {
            $publicUrl = $tunnels.tunnels[0].public_url
            Write-Host "Public URL:" $publicUrl
            Write-Host "Dashboard:" ($publicUrl + '/dashboard')
            Write-Host "Publish endpoint (protected):" ($publicUrl + '/publish?token=' + $PublishToken)
            # open in default browser
            Start-Process $publicUrl
            Pop-Location
            exit 0
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

Write-Warning "Timed out waiting for ngrok. Check ngrok status or run 'ngrok http 8080' manually. Server is running locally at http://localhost:8080"
Pop-Location
exit 1
