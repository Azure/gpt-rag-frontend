import json
import logging
import os
import time
from urllib.parse import unquote

import requests
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

load_dotenv()

# Helper functions for reading environment variables
def read_env_variable(var_name, default=None):
    value = os.getenv(var_name, default)
    return value.strip() if value else default

def read_env_list(var_name):
    value = os.getenv(var_name, "")
    return [item.strip() for item in value.split(",") if item.strip()]

# Read Environment Variables
SPEECH_REGION = read_env_variable('SPEECH_REGION')
ORCHESTRATOR_ENDPOINT = read_env_variable('ORCHESTRATOR_ENDPOINT')
STORAGE_ACCOUNT = read_env_variable('STORAGE_ACCOUNT')
LOGLEVEL = read_env_variable('LOGLEVEL', 'INFO').upper()

ALLOWED_GROUP_NAMES = read_env_list('ALLOWED_GROUP_NAMES')
ALLOWED_USER_PRINCIPALS = read_env_list('ALLOWED_USER_PRINCIPALS')
ALLOWED_USER_NAMES = read_env_list('ALLOWED_USER_NAMES')

SPEECH_RECOGNITION_LANGUAGE = read_env_variable('SPEECH_RECOGNITION_LANGUAGE')
SPEECH_SYNTHESIS_LANGUAGE = read_env_variable('SPEECH_SYNTHESIS_LANGUAGE')
SPEECH_SYNTHESIS_VOICE_NAME = read_env_variable('SPEECH_SYNTHESIS_VOICE_NAME')

# Set logging
logging.basicConfig(level=LOGLEVEL)

# Obtain the token using Managed Identity
def get_managed_identity_token():
    credential = DefaultAzureCredential()
    token = credential.get_token("https://management.azure.com/.default").token
    return token

def get_function_key():
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
    resource_group = os.getenv('AZURE_RESOURCE_GROUP_NAME')
    function_app_name = os.getenv('AZURE_ORCHESTRATOR_FUNC_NAME')
    token = get_managed_identity_token()
    logging.info("[webbackend] Obtaining function key.")
    
    # URL to get all function keys, including the default one
    requestUrl = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Web/sites/{function_app_name}/functions/orc/listKeys?api-version=2022-03-01"
    
    requestHeaders = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(requestUrl, headers=requestHeaders)
    response_json = json.loads(response.content.decode('utf-8'))
    
    try:
        # Assuming you want to get the 'default' key
        function_key = response_json['default']
    except KeyError as e:
        function_key = None
        logging.error(f"[webbackend] Error when getting function key. Details: {str(e)}.")
    
    return function_key

app = Flask(__name__)
CORS(app)

@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def static_file(path):
    return app.send_static_file(path)

def check_authorization(request):
    client_principal_id = request.headers.get('X-MS-CLIENT-PRINCIPAL-ID')
    client_principal_name = request.headers.get('X-MS-CLIENT-PRINCIPAL-NAME')
    logging.info(f"[webbackend] User principal: {client_principal_id}")
    logging.info(f"[webbackend] User name: {client_principal_name}")
    
    # Initialize groups list
    groups = []
    
    # Try to get groups from Graph API
    access_token = request.headers.get('X-MS-TOKEN-AAD-ACCESS-TOKEN')
    if access_token:
        try:
            graph_headers = {
                'Authorization': f'Bearer {access_token}'
            }
            graph_url = 'https://graph.microsoft.com/v1.0/me/memberOf'
            graph_response = requests.get(graph_url, headers=graph_headers)
            graph_response.raise_for_status()
            group_data = graph_response.json()
            groups_from_graph = [group.get('displayName', '') for group in group_data.get('value', [])]
            groups.extend(groups_from_graph)  # Add groups from Graph API to the list
            logging.info(f"[webbackend] User groups from Graph API: {groups_from_graph}")
        except Exception as e:
            logging.info(f"[webbackend] Failed to get user groups from Graph API: {e}")
    else:
        logging.info("[webbackend] No access token found in headers; cannot get user groups")

    # Log the ALLOWED_GROUPS and ALLOWED_USERS for debugging
    logging.info(f"[webbackend] Allowed user groups: {'any' if not ALLOWED_GROUP_NAMES else ALLOWED_GROUP_NAMES}")
    logging.info(f"[webbackend] Allowed user principals: {'any' if not ALLOWED_USER_PRINCIPALS else ALLOWED_USER_PRINCIPALS}")
    logging.info(f"[webbackend] Allowed user names: {'any' if not ALLOWED_USER_NAMES else ALLOWED_USER_NAMES}")
    
    # Check authorization
    authorized = True
    if ALLOWED_GROUP_NAMES or ALLOWED_USER_PRINCIPALS or ALLOWED_USER_NAMES:
        authorized = False
        if client_principal_name in ALLOWED_USER_NAMES:
            authorized = True
        elif client_principal_id in ALLOWED_USER_PRINCIPALS:
            authorized = True
        elif any(group in ALLOWED_GROUP_NAMES for group in groups):
            authorized = True
        if not authorized:
            logging.info("[webbackend] User does not belong to any of the allowed groups or is not an allowed user")
    
    # Return a dictionary with all relevant information
    return {
        'authorized': authorized,
        'client_principal_id': client_principal_id,
        'client_principal_name': client_principal_name,
        'client_group_names': groups
    }

@app.route("/chatgpt", methods=["POST"])
def chatgpt():
    start_time = time.time()  # Start the timer    
    conversation_id = request.json["conversation_id"]
    question = request.json["query"]
    file = request.json["file"]
    logging.info(f"[webbackend] from orchestrator file : {file}") 
    
    logging.info("[webbackend] conversation_id: " + conversation_id)    
    logging.info("[webbackend] question: " + question)
    
    # Check authorization
    auth_info = check_authorization(request)
    
    if not auth_info['authorized']:
        response = {
            "answer": "You are not authorized to access this service. Please contact your administrator.",
            "thoughts": "The user attempted to access the service but is not part of any authorized users or groups.",
            "conversation_id": conversation_id
        }
        return jsonify(response)
    
    # Extract user information
    client_principal_id = auth_info['client_principal_id']
    client_principal_name = auth_info['client_principal_name']
    client_group_names = auth_info['client_group_names']
    
    # Call orchestrator
    function_key = get_function_key()
        
    try:
        url = ORCHESTRATOR_ENDPOINT
        payload = {
            "conversation_id": conversation_id,
            "question": question,
            "client_principal_id": client_principal_id,
            "client_principal_name": client_principal_name,
            "client_group_names": client_group_names
        }
        headers = {
            'Content-Type': 'application/json',
            'x-functions-key': function_key  
        }
        logging.info(f"[webbackend] calling orchestrator at: {ORCHESTRATOR_ENDPOINT}")        
        response = requests.get(url, headers=headers, json=payload)
        logging.info(f"[webbackend] response: {response.text[:100]}...") 
        return response.text
    except Exception as e:
        logging.error("[webbackend] exception in /chatgpt")
        logging.exception(e)
        response = {
            "answer": "Error in application backend.",
            "thoughts": "",
            "conversation_id": conversation_id
        }
        return jsonify(response)
    finally:
        end_time = time.time()  # End the timer
        duration = end_time - start_time
        logging.info(f"[webbackend] Finished processing in {duration:.2f} seconds")

# Methods to provide access to speech services and blob storage account blobs

@app.route("/api/get-speech-token", methods=["GET"])
def getGptSpeechToken():
    try:
        token = get_managed_identity_token()
        fetch_token_url = f"https://{SPEECH_REGION}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(fetch_token_url, headers=headers)
        access_token = str(response.text)
        return json.dumps({
            'token': access_token,
            'region': SPEECH_REGION,
            'speechRecognitionLanguage': SPEECH_RECOGNITION_LANGUAGE,
            'speechSynthesisLanguage': SPEECH_SYNTHESIS_LANGUAGE,
            'speechSynthesisVoiceName': SPEECH_SYNTHESIS_VOICE_NAME
        })
    except Exception as e:
        logging.exception("[webbackend] exception in /api/get-speech-token")
        return jsonify({"error": str(e)}), 500

@app.route("/api/upload-blob", methods=["POST"])
def uploadBlob():
    try:
        # Retrieve the file from the request
        uploaded_file = request.files['file']
        if not uploaded_file:
            return jsonify({"error": "No file provided."}), 400

        # Generate a blob name (you can customize this)
        blob_name = uploaded_file.filename

        # Authenticate with Azure Blob Storage
        client_credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(
            f"https://{STORAGE_ACCOUNT}.blob.core.windows.net",
            client_credential
        )

        # Get a blob client
        blob_client = blob_service_client.get_blob_client(container='attachments', blob=blob_name)

        # Upload the file
        blob_client.upload_blob(uploaded_file.read(), overwrite=True)
        logging.info(f"Successfully uploaded blob: {blob_name}")

        # Return the blob name
        return jsonify({"blob_name": blob_name}), 200

    except Exception as e:
        logging.exception("[webbackend] exception in /api/upload-blob")
        return jsonify({"error": str(e)}), 500

@app.route("/api/get-storage-account", methods=["GET"])
def getStorageAccount():
    if not STORAGE_ACCOUNT:
        return jsonify({"error": "Add STORAGE_ACCOUNT to frontend app settings"}), 500
    try:
        return json.dumps({'storageaccount': STORAGE_ACCOUNT})
    except Exception as e:
        logging.exception("[webbackend] exception in /api/get-storage-account")
        return jsonify({"error": str(e)}), 500

@app.route("/api/get-blob", methods=["POST"])
def getBlob():
    blob_name = unquote(request.json["blob_name"])
    container = request.json["container"]

    logging.info(f"Starting getBlob function for blob: {blob_name}")
    try:
        client_credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(
            f"https://{STORAGE_ACCOUNT}.blob.core.windows.net",
            client_credential
        )
        if not container :
            container = 'documents'
        blob_client = blob_service_client.get_blob_client(container=container, blob=blob_name)
        blob_data = blob_client.download_blob()
        blob_text = blob_data.readall()
        logging.info(f"Successfully fetched blob: {blob_name}")
        return Response(blob_text, content_type='application/octet-stream')
    except Exception as e:
        logging.exception("[webbackend] exception in /api/get-blob")
        logging.exception(blob_name)
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
