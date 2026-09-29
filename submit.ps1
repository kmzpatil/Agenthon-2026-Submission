param (
    [Parameter(Mandatory=$true)][string]$GithubUsername,
    [Parameter(Mandatory=$true)][int]$TeamNumber,
    [Parameter(Mandatory=$true)][string]$TeamKey,
    [Parameter(Mandatory=$true)][ValidateSet("T1", "T3")][string]$Track
)

$ErrorActionPreference = "Stop"

# Set configuration based on Track
$ImageName = "ghcr.io/$($GithubUsername.ToLower())/agenthon-$( $Track.ToLower() )"
$ImageTag = "$ImageName`:latest"
$Context = if ($Track -eq "T1") { "T1_Coder_Agent" } else { "T3_Simulation" }
$CompId = if ($Track -eq "T1") { "agenthon2026-coding-dev" } else { "agenthon2026-simulation-dev" }
$Category = if ($Track -eq "T1") { "api" } else { "simulator" }
$TrackName = if ($Track -eq "T1") { "coding" } else { "simulation" }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Agenthon 2026 Auto-Submission Packager" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Build Docker Image
Write-Host "`n[1/5] Building Docker image $ImageTag from ./$Context..." -ForegroundColor Yellow
docker build -t $ImageTag ./$Context

# 2. Push Docker Image
Write-Host "`n[2/5] Pushing to GHCR (Ensure you are authenticated via 'docker login ghcr.io')..." -ForegroundColor Yellow
docker push $ImageTag

# 3. Retrieve SHA256 Digest
Write-Host "`n[3/5] Retrieving SHA256 Digest from registry..." -ForegroundColor Yellow
$Digest = docker inspect --format='{{index .RepoDigests 0}}' $ImageTag
if (-not $Digest) {
    Write-Host "Failed to retrieve digest. Ensure the docker push was successful." -ForegroundColor Red
    exit 1
}
$DigestHash = $Digest.Split("@")[1]
Write-Host "Digest found: $DigestHash" -ForegroundColor Green

# 4. Generate submission.json dynamically
Write-Host "`n[4/5] Generating submission.json..." -ForegroundColor Yellow
$SubmissionJson = @"
{
  "schema_version": "1.1.0",
  "interface_version": "2.0",
  "competition_id": "$CompId",
  "track": "$TrackName",
  "phase": "dev",
  "category": "$Category",
  "image_access": "public",
  "models": [],
  "license": "MIT",
  "image": {
    "registry": "ghcr.io",
    "repository": "$($GithubUsername.ToLower())/agenthon-$( $Track.ToLower() )",
    "digest": "$DigestHash"
  }
}
"@
Set-Content -Path "submission.json" -Value $SubmissionJson

# 5. Install Toolkit
Write-Host "`n[5/5] Installing official qfbench2-common toolkit..." -ForegroundColor Yellow
pip install "qfbench2-common @ git+https://github.com/Agenthon-2026/Agenthon2026-public.git@v2.4.4#subdirectory=common" -q

# 6. Package final ZIP
Write-Host "`nPackaging final ZIP via qfbench2..." -ForegroundColor Yellow
$KeyFile = "temp_team_key.txt"
Set-Content -Path $KeyFile -Value $TeamKey
qfbench2 submission pack --descriptor submission.json --team-number $TeamNumber --team-key-file $KeyFile --out "submission_${Track}.zip"
Remove-Item $KeyFile

Write-Host "`nSUCCESS! Your submission file 'submission_${Track}.zip' is ready!" -ForegroundColor Green
Write-Host "Upload this file directly to CodaBench." -ForegroundColor Green
