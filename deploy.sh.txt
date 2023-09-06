#!/bin/bash

# Check if user is logged in
if ! az account show > /dev/null 2>&1; then
    echo "Please log in with 'az login' before running this script." 
    echo "If running the script on an Azure VM with managed identity set use 'az login -i'"
    echo "If you have access to multiple tenants use 'az login --tenant TENANT_ID' to specify the tenant where the resource group and web app are located."    
    exit 1
fi

# Ask for resource group name
read -p "Enter resource group name: " resourcegroupname

# Ask for web app name
read -p "Enter web app name: " webappname

# Check if Node.js is installed
if ! command -v node > /dev/null 2>&1; then
    echo "Node.js is not installed."
    echo "Install Node.js 18"    
    exit 1
fi

# Check if Node.js version is greater than 16
if [[ $(node -v | sed 's/v//g' | cut -d. -f1) -lt 16 ]]; then
    echo "Node.js version is not greater than 16."
    read -p "Do you want to run the upgrade commands? (y/n) " answer
    if [[ $answer == [yY] ]]; then
        echo "Running upgrade commands..."
        npm cache clean -f
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
        source ~/.bashrc
        nvm install 18
        nvm use 18
    else
        echo "Aborting deployment."
        exit 1
    fi
fi

# Deploy
cd frontend
npm install
npm run build
cd ../backend && zip -r ../deploy.zip *
cd ..
az webapp deploy --resource-group $resourcegroupname --name $webappname --src-path deploy.zip --type zip --async true

echo "Done. If succeeded you can now browse to https://$webappname.azurewebsites.net"	