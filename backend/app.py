import os
import logging
import requests
import json
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from urllib.parse import unquote
from urllib.parse import urlparse

load_dotenv()

SPEECH_REGION = os.getenv('SPEECH_REGION')
ORCHESTRATOR_ENDPOINT = os.getenv('ORCHESTRATOR_ENDPOINT')
STORAGE_ACCOUNT = os.getenv('STORAGE_ACCOUNT')
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)

def get_managed_identity_token():
    # Obtain the token using Managed Identity
    credential = DefaultAzureCredential()
    token = credential.get_token("https://management.azure.com/.default").token
    return token

def get_function_key():
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
    resource_group = os.getenv('AZURE_RESOURCE_GROUP_NAME')
    function_app_name = os.getenv('AZURE_ORCHESTRATOR_FUNC_NAME')
    token = get_managed_identity_token()
    logging.info(f"[webbackend] Obtaining function key.")
    requestUrl = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Web/sites/{function_app_name}/functions/orc/keys/mykey?api-version=2022-03-01"
    requestHeaders = {
        "Authorization": f"Bearer {token}" ,
        "Content-Type": "application/json"
    }
    data = {
        'properties': {}
    }
    response = requests.put(requestUrl, headers=requestHeaders, data=json.dumps(data))
    response_json = json.loads(response.content.decode('utf-8'))
    try:
        function_key = response_json['properties']['value']
    except Exception as e:
        function_key = None
        logging.error(f"[webbackend] Error when getting function key. Details: {str(e)}.")        
    return function_key


SPEECH_RECOGNITION_LANGUAGE = os.getenv('SPEECH_RECOGNITION_LANGUAGE')
SPEECH_SYNTHESIS_LANGUAGE = os.getenv('SPEECH_SYNTHESIS_LANGUAGE')
SPEECH_SYNTHESIS_VOICE_NAME = os.getenv('SPEECH_SYNTHESIS_VOICE_NAME')

app = Flask(__name__)
CORS(app)

@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def static_file(path):
    return app.send_static_file(path)

@app.route("/chatgpt", methods=["POST"])
def chatgpt():
    conversation_id = request.json["conversation_id"]
    question = request.json["query"]
    client_principal_id = request.headers.get('X-MS-CLIENT-PRINCIPAL-ID')
    client_principal_name = request.headers.get('X-MS-CLIENT-PRINCIPAL-NAME')
    logging.info("[webbackend] conversation_id: " + conversation_id)    
    logging.info("[webbackend] question: " + question)
    logging.info(f"[webbackend] User principal: {client_principal_id}")
    logging.info(f"[webbackend] User name: {client_principal_name}")

    function_key = get_function_key()
        
    try:
        url = ORCHESTRATOR_ENDPOINT
        payload = json.dumps({
            "conversation_id": conversation_id,
            "question": question,
            "client_principal_id": client_principal_id,
            "client_principal_name": client_principal_name
        })
        headers = {
            'Content-Type': 'application/json',
            'x-functions-key': function_key  
        }
        logging.info(f"[webbackend] calling orchestrator at: {ORCHESTRATOR_ENDPOINT}")        
        response = requests.request("GET", url, headers=headers, data=payload)
        logging.info(f"[webbackend] response: {response.text[:100]}...") 
        return(response.text)
    except Exception as e:
        logging.exception("[webbackend] exception in /chatgpt")
        return jsonify({"error": str(e)}), 500
    

# methods to provide access to speech services and blob storage account blobs

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
        return json.dumps({'token': access_token, 'region': SPEECH_REGION, 'speechRecognitionLanguage': SPEECH_RECOGNITION_LANGUAGE, 'speechSynthesisLanguage': SPEECH_SYNTHESIS_LANGUAGE, 'speechSynthesisVoiceName': SPEECH_SYNTHESIS_VOICE_NAME})
    except Exception as e:
        logging.exception("[webbackend] exception in /api/get-speech-token")
        return jsonify({"error": str(e)}), 500

@app.route("/api/get-storage-account", methods=["GET"])
def getStorageAccount():
    if STORAGE_ACCOUNT is None or STORAGE_ACCOUNT == '':
        return jsonify({"error": "Add STORAGE_ACCOUNT to frontend app settings"}), 500
    try:
        return json.dumps({'storageaccount': STORAGE_ACCOUNT})
    except Exception as e:
        logging.exception("[webbackend] exception in /api/get-storage-account")
        return jsonify({"error": str(e)}), 500

@app.route("/api/get-blob", methods=["POST"])
def getBlob():
    logging.exception ("------------------ENTRA ------------")
    blob_name = unquote(request.json["blob_name"])
    try:
        client_credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(
            f"https://{STORAGE_ACCOUNT}.blob.core.windows.net",
            client_credential
        )
        blob_client = blob_service_client.get_blob_client(container='documents', blob=blob_name)
        blob_data = blob_client.download_blob()
        blob_text = blob_data.readall()
        return Response(blob_text, content_type='application/octet-stream')
    except Exception as e:
        logging.exception("[webbackend] exception in /api/get-blob")
        logging.exception(blob_name)
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
