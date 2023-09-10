import os
import mimetypes
import time
import logging
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

load_dotenv()

SPEECH_REGION = os.getenv('SPEECH_REGION')
ORCHESTRATOR_ENDPOINT = os.getenv('ORCHESTRATOR_ENDPOINT')
ORCHESTRATOR_URI = os.getenv('ORCHESTRATOR_URI')
STORAGE_ACCOUNT = os.getenv('STORAGE_ACCOUNT')

def get_secret(secretName):
    keyVaultName = os.environ["AZURE_KEY_VAULT_NAME"]
    KVUri = f"https://{keyVaultName}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KVUri, credential=credential)
    logging.info(f"[webbackend] retrieving {secretName} secret from {keyVaultName}.")   
    retrieved_secret = client.get_secret(secretName)
    return retrieved_secret.value

# def get_token(scope):
#     credential = DefaultAzureCredential()
#     logging.info(f"[webbackend] retrieving token , scope: {scope}.")
#     token = ""
#     try:
#         token = credential.get_token(f"{scope}").token
#     except Exception as e:
#         logging.error(f"[webbackend] error when retrieving security token {str(e)}.")
#     return token

SPEECH_KEY = get_secret('speechKey')

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
    logging.info("[webbackend] conversation_id: " + conversation_id)    
    logging.info("[webbackend] question: " + question)

    # scope = '<replace by orchestrator app id>/.default' 
    # token=get_token(scope)
    functionKey = get_secret('host--functionKey--default')
    
    try:
        url = ORCHESTRATOR_ENDPOINT
        payload = json.dumps({
            "conversation_id": conversation_id,
            "question": question
        })
        headers = {
            'Content-Type': 'application/json',
            'x-functions-key': functionKey  
            # 'Authorization': "Bearer " + token          
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        print(response.text)
        return(response.text)
    except Exception as e:
        logging.exception("[webbackend] exception in /chatgpt")
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/get-speech-token", methods=["GET"])
def getGptSpeechToken():
    try:
        fetch_token_url = f"https://{SPEECH_REGION}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        headers = {
            'Ocp-Apim-Subscription-Key': SPEECH_KEY,
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
