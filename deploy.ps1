# File to store environment variables
$ENV_FILE = "deploy.env"

# Load existing values from .env file if it exists
if (Test-Path $ENV_FILE) {
    $envVars = Get-Content $ENV_FILE | ForEach-Object {
        $keyValue = $_ -split "="
        Set-Item -Path Env:\$($keyValue[0]) -Value $keyValue[1]
    }
}

# Prompt the user for Azure details, using the stored values if available
$SUBSCRIPTION_ID = Read-Host "Enter your Azure Subscription ID [${env:SUBSCRIPTION_ID}]"
if (-not $SUBSCRIPTION_ID) { $SUBSCRIPTION_ID = $env:SUBSCRIPTION_ID }

$RESOURCE_GROUP_NAME = Read-Host "Enter your Azure Resource Group Name [${env:RESOURCE_GROUP_NAME}]"
if (-not $RESOURCE_GROUP_NAME) { $RESOURCE_GROUP_NAME = $env:RESOURCE_GROUP_NAME }

$WEB_APP_NAME = Read-Host "Enter your Azure Web App Name [${env:WEB_APP_NAME}]"
if (-not $WEB_APP_NAME) { $WEB_APP_NAME = $env:WEB_APP_NAME }

# Save the entered values to the deploy.env file for future use
Write-Host "Saving environment variables..."
@"
SUBSCRIPTION_ID=$SUBSCRIPTION_ID
RESOURCE_GROUP_NAME=$RESOURCE_GROUP_NAME
WEB_APP_NAME=$WEB_APP_NAME
"@ | Set-Content $ENV_FILE

# Step 1: Build Frontend
Write-Host "Building frontend..."
Set-Location "frontend"
if (-not (Test-Path "package.json")) {
    Write-Host "Frontend folder not found!" -ForegroundColor Red
    exit 1
}

# Install dependencies and build the frontend
npm install
if (-not $?) { Write-Host "Frontend build failed!" -ForegroundColor Red; exit 1 }
npm run build
if (-not $?) { Write-Host "Frontend build failed!" -ForegroundColor Red; exit 1 }

Set-Location "../"

# Step 2: Prepare for deployment
Write-Host "Preparing for deployment..."

# Move to the backend folder
if (-not (Test-Path "backend")) {
    Write-Host "Backend folder not found!" -ForegroundColor Red
    exit 1
}
Set-Location "backend"

# Remove backend_env if it exists
if (Test-Path "backend_env") {
    Write-Host "Removing backend_env..."
    Remove-Item -Recurse -Force "backend_env"
    if (-not $?) { Write-Host "Failed to remove backend_env" -ForegroundColor Red; exit 1 }
}

# Step 3: Zip backend source code
Write-Host "Zipping backend source code..."
if (Test-Path "../deploy.zip") {
    Write-Host "Removing existing deploy.zip file..."
    Remove-Item -Force "../deploy.zip"
}
Compress-Archive -Path * -DestinationPath "../deploy.zip" -Force
if (-not $?) { Write-Host "Failed to zip backend code!" -ForegroundColor Red; exit 1 }
Set-Location ..

# Step 4: Deploy to Azure
Write-Host "Deploying to Azure Web App..."
az webapp deploy `
  --subscription $SUBSCRIPTION_ID `
  --resource-group $RESOURCE_GROUP_NAME `
  --name $WEB_APP_NAME `
  --src-path "deploy.zip" `
  --type zip `
  --async true
if (-not $?) { Write-Host "Deployment failed!" -ForegroundColor Red; exit 1 }

Write-Host "Deployment started. You can check the status in the Azure portal."
