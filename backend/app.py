import os
import mimetypes
import time
import logging
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

SPEECH_KEY = os.getenv('SPEECH_KEY')
SPEECH_REGION = os.getenv('SPEECH_REGION')
ORCHESTRATOR_ENDPOINT = os.getenv('ORCHESTRATOR_ENDPOINT')
FUNCTION_KEY = os.getenv('FUNCTION_KEY')
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
    print(conversation_id)
    print(question)
    try:
        url = ORCHESTRATOR_ENDPOINT
        payload = json.dumps({
            "conversation_id": conversation_id,
            "question": question
        })
        headers = {
            'x-functions-key': FUNCTION_KEY,
            'Content-Type': 'application/json'
        }
        
        response = requests.request("GET", url, headers=headers, data=payload)
        print(response.text)
        return(response.text)
    except Exception as e:
        logging.exception("Exception in /chatgpt")
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
        logging.exception("Exception in /api/get-speech-token")
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
