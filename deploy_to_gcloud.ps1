# PowerShell script for Google Cloud deployment
# Usage: .\deploy_to_gcloud.ps1

Write-Host "=== EVE Echoes Calculator - Google Cloud Deployment ===" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ID = Read-Host "Enter your Google Cloud Project ID"
$REGION = "europe-central2"  # Warsaw
$SERVICE_NAME = "eve-echoes-calculator"

Write-Host ""
Write-Host "Choose deployment option:" -ForegroundColor Yellow
Write-Host "1. Cloud Run (Recommended - Serverless, pay per use)"
Write-Host "2. App Engine (Simple, automatic scaling)"
Write-Host "3. Exit"
Write-Host ""

$choice = Read-Host "Enter your choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Deploying to Cloud Run..." -ForegroundColor Green
        
        # Enable required APIs
        Write-Host "Enabling required APIs..." -ForegroundColor Yellow
        gcloud services enable run.googleapis.com
        gcloud services enable cloudbuild.googleapis.com
        gcloud services enable containerregistry.googleapis.com
        
        # Build container image
        Write-Host "Building container image..." -ForegroundColor Yellow
        gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME
        
        # Deploy to Cloud Run
        Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow
        gcloud run deploy $SERVICE_NAME `
            --image gcr.io/$PROJECT_ID/$SERVICE_NAME `
            --platform managed `
            --region $REGION `
            --allow-unauthenticated `
            --memory 2Gi `
            --cpu 2 `
            --port 8080 `
            --max-instances 10 `
            --min-instances 0
        
        Write-Host ""
        Write-Host "Deployment complete!" -ForegroundColor Green
        Write-Host "Your app will be available at the URL shown above." -ForegroundColor Cyan
    }
    
    "2" {
        Write-Host ""
        Write-Host "Deploying to App Engine..." -ForegroundColor Green
        
        # Check if App Engine is created
        $appInfo = gcloud app describe 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Creating App Engine application..." -ForegroundColor Yellow
            gcloud app create --region=$REGION
        }
        
        # Enable required APIs
        Write-Host "Enabling required APIs..." -ForegroundColor Yellow
        gcloud services enable appengine.googleapis.com
        
        # Deploy to App Engine
        Write-Host "Deploying to App Engine..." -ForegroundColor Yellow
        gcloud app deploy app.yaml --quiet
        
        Write-Host ""
        Write-Host "Deployment complete!" -ForegroundColor Green
        Write-Host "Opening your app in browser..." -ForegroundColor Cyan
        gcloud app browse
    }
    
    "3" {
        Write-Host "Deployment cancelled." -ForegroundColor Yellow
        exit
    }
    
    default {
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
        exit
    }
}

Write-Host ""
Write-Host "=== Deployment Information ===" -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID"
Write-Host "Region: $REGION"
Write-Host "Service: $SERVICE_NAME"
Write-Host ""
Write-Host "To view logs, run:" -ForegroundColor Yellow
if ($choice -eq "1") {
    Write-Host "gcloud run services logs read $SERVICE_NAME --region $REGION"
} else {
    Write-Host "gcloud app logs tail"
}
Write-Host ""
Write-Host "Remember to support the developer!" -ForegroundColor Green
Write-Host "Send ISK donations to: lawrokhPL in EVE Echoes" -ForegroundColor Cyan
