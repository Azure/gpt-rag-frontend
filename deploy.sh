#!/bin/bash

# File to store environment variables
ENV_FILE="deploy.env"

# Load existing values from .env file if it exists
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
fi

# Prompt the user for Azure details, using the stored values if available
read -p "Enter your Azure Subscription ID [${SUBSCRIPTION_ID:-not set}]: " input_subscription_id
SUBSCRIPTION_ID=${input_subscription_id:-$SUBSCRIPTION_ID}

read -p "Enter your Azure Resource Group Name [${RESOURCE_GROUP_NAME:-not set}]: " input_resource_group
RESOURCE_GROUP_NAME=${input_resource_group:-$RESOURCE_GROUP_NAME}

read -p "Enter your Azure Web App Name [${WEB_APP_NAME:-not set}]: " input_web_app
WEB_APP_NAME=${input_web_app:-$WEB_APP_NAME}

# Save the entered values to the deploy.env file for future use
echo "Saving environment variables..."
cat <<EOF > "$ENV_FILE"
SUBSCRIPTION_ID=$SUBSCRIPTION_ID
RESOURCE_GROUP_NAME=$RESOURCE_GROUP_NAME
WEB_APP_NAME=$WEB_APP_NAME
EOF

# Step 1: Build Frontend
echo "Building frontend..."
cd frontend || { echo "Frontend folder not found!"; exit 1; }

# Install dependencies and build the frontend
npm install
npm run build || { echo "Frontend build failed!"; exit 1; }

# Step 2: Prepare for deployment
echo "Preparing for deployment..."

# Move to the backend folder
cd ../backend || { echo "Backend folder not found!"; exit 1; }

# Remove backend_env if it exists
if [ -d "backend_env" ]; then
    echo "Removing backend_env..."
    rm -rf backend_env || { echo "Failed to remove backend_env"; exit 1; }
fi

# Step 3: Zip backend source code
echo "Zipping backend source code..."
zip -r ../deploy.zip *  || { echo "Failed to zip backend code"; exit 1; }
cd .. || exit

# Step 4: Deploy to Azure
echo "Deploying to Azure Web App..."
az webapp deploy \
  --subscription "$SUBSCRIPTION_ID" \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --name "$WEB_APP_NAME" \
  --src-path deploy.zip \
  --type zip \
  --async true || { echo "Deployment failed!"; exit 1; }

echo "Deployment started. You can check the status in the Azure portal."
