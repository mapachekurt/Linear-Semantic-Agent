# fix_iam.ps1
$PROJECT_ID = "linear-semantic-agents"
$SA_NAME = "linear-semantic-agent"
$SA_EMAIL = "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

Write-Host "Auditing and fixing IAM permissions for $SA_EMAIL..." -ForegroundColor Yellow

# Ensure Service Account exists
if (!(gcloud iam service-accounts list --filter="email:$SA_EMAIL" --format="value(email)")) {
    Write-Host "Creating service account $SA_NAME..." -ForegroundColor Cyan
    gcloud iam service-accounts create $SA_NAME --display-name="Linear Semantic Agent"
}

# Roles required for the Agent Service Account
$roles = @(
    "roles/aiplatform.user",
    "roles/datastore.user",
    "roles/secretmanager.secretAccessor",
    "roles/storage.objectAdmin",
    "roles/aiplatform.reasoningEngineServiceAgent"
)

foreach ($role in $roles) {
    Write-Host "Granting $role to $SA_EMAIL..." -ForegroundColor Cyan
    gcloud projects add-iam-policy-binding $PROJECT_ID `
        --member="serviceAccount:$SA_EMAIL" `
        --role="$role" `
        --condition=None | Out-Null
}

# Ensure the user has the 'iam.serviceAccounts.actAs' permission on the SA
$userEmail = gcloud auth list --filter=status:ACTIVE --format="value(account)"
Write-Host "Granting serviceAccountUser role to $userEmail for $SA_EMAIL..." -ForegroundColor Cyan
gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL `
    --member="user:$userEmail" `
    --role="roles/iam.serviceAccountUser" | Out-Null

# Create Staging Bucket if it doesn't exist
$BUCKET_NAME = "linear-semantic-agents-staging"
if (!(gsutil ls -b "gs://$BUCKET_NAME" 2>$null)) {
    Write-Host "Creating staging bucket gs://$BUCKET_NAME..." -ForegroundColor Cyan
    gsutil mb -l us-central1 "gs://$BUCKET_NAME"
}

Write-Host "IAM permissions and staging bucket setup complete!" -ForegroundColor Green
