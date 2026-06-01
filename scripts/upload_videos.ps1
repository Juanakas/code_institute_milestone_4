<#
.SYNOPSIS
  Set environment variables and invoke the Python uploader for S3 / R2.

.DESCRIPTION
  This wrapper sets optional AWS/R2 credentials and `VIDEO_LOCAL_DIR`, builds
  the command-line for `scripts/upload_videos.py` and runs it.

.EXAMPLE
  .\scripts\upload_videos.ps1 -Bucket my-r2-bucket -LocalDir videos2 -Provider r2 -EndpointUrl 'https://<acct>.r2.cloudflarestorage.com' -PublicBaseUrl 'https://cdn.example.com/videos' -AccessKey <KEY> -SecretKey <SECRET>
#>

param(
    [Parameter(Mandatory=$true)] [string] $Bucket,
    [string] $LocalDir = "videos2",
    [ValidateSet("s3","r2")] [string] $Provider = "r2",
    [string] $EndpointUrl = "",
    [string] $PublicBaseUrl = "",
    [string] $Acl = "public-read",
    [string] $AccessKey = "",
    [string] $SecretKey = "",
    [string] $SessionToken = "",
    [switch] $DryRun
)

Set-StrictMode -Version Latest

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Err($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

# Set AWS credentials in the environment if provided (works for both S3 and R2)
if ($AccessKey) { $env:AWS_ACCESS_KEY_ID = $AccessKey; Write-Info "Set AWS_ACCESS_KEY_ID" }
if ($SecretKey) { $env:AWS_SECRET_ACCESS_KEY = $SecretKey; Write-Info "Set AWS_SECRET_ACCESS_KEY" }
if ($SessionToken) { $env:AWS_SESSION_TOKEN = $SessionToken; Write-Info "Set AWS_SESSION_TOKEN" }

# Resolve local directory: accept either an absolute path or a project-relative folder
try {
    if (Test-Path $LocalDir) {
        $fullLocal = (Resolve-Path $LocalDir).Path
    } else {
        $candidate = Join-Path -Path (Resolve-Path $PSScriptRoot\..) -ChildPath $LocalDir
        if (Test-Path $candidate) { $fullLocal = (Resolve-Path $candidate).Path } else { Write-Err "Local dir not found: $LocalDir"; exit 2 }
    }
} catch {
    Write-Err "Failed to resolve local dir: $_"; exit 2
}

$env:VIDEO_LOCAL_DIR = $fullLocal
Write-Info "VIDEO_LOCAL_DIR=$fullLocal"

# Build argument list for the Python uploader
$uploader = Join-Path $PSScriptRoot 'upload_videos.py'
if (-not (Test-Path $uploader)) { Write-Err "Uploader not found: $uploader"; exit 2 }

$argsList = @('--local-dir', $fullLocal, '--bucket', $Bucket, '--provider', $Provider)
if ($EndpointUrl) { $argsList += @('--endpoint-url', $EndpointUrl) }
if ($PublicBaseUrl) { $argsList += @('--public-base-url', $PublicBaseUrl) }
if ($Acl) { $argsList += @('--acl', $Acl) }
if ($DryRun.IsPresent) { $argsList += '--dry-run' }

Write-Info "Invoking uploader: python $uploader $($argsList -join ' ')"

try {
    & python $uploader @argsList
    $exit = $LASTEXITCODE
} catch {
    Write-Err "Uploader execution failed: $_"
    exit 3
}

if ($exit -ne 0) { Write-Err "Uploader returned exit code $exit"; exit $exit }

Write-Info "Upload completed successfully."

if ($PublicBaseUrl) {
    Write-Host "To deploy, set VIDEO_BASE_URL on Heroku:"
    Write-Host "heroku config:set VIDEO_BASE_URL=$PublicBaseUrl --app <your-app-name>"
}
