# validate_env.ps1
Write-Host "Checking GCP environment..." -ForegroundColor Yellow

# Check gcloud
if (!(Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Error "gcloud CLI not found. Please install it: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Check Project
$projectId = gcloud config get-value project
if ([string]::IsNullOrWhiteSpace($projectId) -or $projectId -eq "(unset)") {
    Write-Error "GCP Project ID not set in gcloud config. Run 'gcloud config set project <PROJECT_ID>'"
    exit 1
}
Write-Host "Using GCP Project: $projectId" -ForegroundColor Green

# Check Auth
$account = gcloud auth list --filter=status:ACTIVE --format="value(account)"
if ([string]::IsNullOrWhiteSpace($account)) {
    Write-Error "No active GCP account found. Run 'gcloud auth login'"
    exit 1
}
Write-Host "Active account: $account" -ForegroundColor Green

# Check APIs
Write-Host "Checking required APIs..." -ForegroundColor Yellow
$apis = @("aiplatform.googleapis.com", "storage.googleapis.com", "firestore.googleapis.com", "secretmanager.googleapis.com")
$enabledApis = gcloud services list --enabled --format="value(config.name)"

foreach ($api in $apis) {
    if ($enabledApis -notcontains $api) {
        Write-Host "Enabling $api..." -ForegroundColor Cyan
        gcloud services enable $api
    } else {
        Write-Host "✓ $api is enabled" -ForegroundColor Green
    }
}

Write-Host "Environment validation complete!" -ForegroundColor Cyan
