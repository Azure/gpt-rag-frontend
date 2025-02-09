#!/usr/bin/env bash
echo "starting script"

# Check if .env file exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file"
    export $(grep -v '^#' .env | xargs)
else
    echo ".env file not found. Please create it."
    exit 1
fi

echo 'Creating python virtual environment "backend/backend_env"'
python -m venv backend/backend_env

# Activate the virtual environment on Windows
source backend/backend_env/Scripts/activate

echo "Restoring backend python packages"
cd backend
./backend_env/Scripts/python -m pip install -r requirements.txt || exit $?

echo "Restoring frontend npm packages"
cd ../frontend
npm install || exit $?

echo "Building frontend"
# Uncomment the line if you want to run the build
# npm run build || exit $?

echo "Starting backend"
cd ../backend
# Open the browser on Windows (assuming the default browser is set)
start http://localhost:8000
./backend_env/Scripts/python ./app.py || exit $?
