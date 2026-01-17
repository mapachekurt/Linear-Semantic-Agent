# deploy.ps1
Write-Host "Starting deployment to Vertex AI Reasoning Engine..." -ForegroundColor Yellow

# Navigate to the agent directory
Set-Location "linear-semantic-agent"

# Ensure dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt | Out-Null

# Run the deployment script
Write-Host "Executing deployment script..." -ForegroundColor Cyan
python deploy_to_reasoning_engine.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment finished successfully!" -ForegroundColor Green
}
else {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}
