import json
import logging
import os
import time
from urllib.parse import unquote
import uuid
import requests

from azure.identity import ManagedIdentityCredential, AzureCliCredential, ChainedTokenCredential
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request, session, redirect, url_for
from flask_cors import CORS
import msal
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

# Helper functions for reading environment variables
def read_env_variable(var_name, default=None):
    value = os.getenv(var_name, default)
    return value.strip() if value else default

def read_env_list(var_name):
    value = os.getenv(var_name, "")
    return [item.strip() for item in value.split(",") if item.strip()]

def read_env_boolean(var_name, default=False):
    value = os.getenv(var_name, str(default)).strip().lower()
    return value in ['true', '1', 'yes']

# Read Environment Variables
SPEECH_REGION = read_env_variable('SPEECH_REGION')
ORCHESTRATOR_ENDPOINT = read_env_variable('ORCHESTRATOR_ENDPOINT')
STORAGE_ACCOUNT = read_env_variable('STORAGE_ACCOUNT')
LOGLEVEL = read_env_variable('LOGLEVEL', 'INFO').upper()

# MSAL / OIDC configuration for custom authentication
ENABLE_AUTHENTICATION = read_env_boolean('ENABLE_AUTHENTICATION')
FORWARD_ACCESS_TOKEN_TO_ORCHESTRATOR = read_env_boolean('FORWARD_ACCESS_TOKEN_TO_ORCHESTRATOR')
OTHER_AUTH_SCOPES = read_env_list('OTHER_AUTH_SCOPES')
CLIENT_ID = os.getenv("CLIENT_ID", "your_client_id")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "your_client_secret")
AUTHORITY = os.getenv("AUTHORITY", "https://login.microsoftonline.com/your_tenant_id")
REDIRECT_PATH = os.getenv("REDIRECT_PATH", "/getAToken")  # Must match the Azure AD app registration redirect URI.
SCOPE = [
    "User.Read"
]

# Authorization settings
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
    credential = ChainedTokenCredential(
        ManagedIdentityCredential(),
        AzureCliCredential()
    )
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
# Remember to set a different secret key in production environments!
app.secret_key = os.getenv("FLASK_SECRET_KEY", "a_very_secret_key")

# Configure server-side session storage
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flask_session_files"
app.config["SESSION_PERMANENT"] = False
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config["PREFERRED_URL_SCHEME"] = "https"

Session(app)

# --- Helper function to obtain a valid (refreshed) access token ---
def get_valid_access_token(scopes):
    cache = _load_cache()
    msal_app = _build_msal_app(cache=cache)
    accounts = msal_app.get_accounts()
    account = accounts[0] if accounts else None
    result = msal_app.acquire_token_silent(scopes, account=account)
    if not result or "error" in result:
        raise Exception(result.get("error_description", "Could not refresh token silently."))
    _save_cache(cache)
    return result.get("access_token")

# --- Authentication Endpoints ---
# Only active if ENABLE_AUTHENTICATION is true.
@app.route("/login")
def login():
    if not ENABLE_AUTHENTICATION:
        return redirect(url_for("index"))
    # Create a unique state for CSRF protection
    session["state"] = str(uuid.uuid4())
    auth_url = _build_auth_url(scopes=SCOPE, state=session["state"])
    return redirect(auth_url)

@app.route(REDIRECT_PATH)
def authorized():
    if not ENABLE_AUTHENTICATION:
        return redirect(url_for("index"))
    
    # Validate state to mitigate CSRF attacks
    if request.args.get("state") != session.get("state"):
        return redirect(url_for("index"))
    if "error" in request.args:
        return f"Error: {request.args.get('error_description')}", 400
    
    if request.args.get("code"):
        logging.info("[webbackend] Attempting to acquire token for user.")        
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
            request.args["code"],
            scopes=SCOPE,
            redirect_uri=url_for("authorized", _external=True)
        )
        if "error" in result:
            logging.warning(f"Could not acquire token for user. Error: {result.get('error_description')}")
            return f"Login failure: {result.get('error_description')}", 400
        
        # Store token and user information in session
        session["user"] = result.get("id_token_claims")
        session["graph_access_token"] = result.get("access_token")
        session["refresh_token"] = result.get("refresh_token")
        _save_cache(cache)

    # For additional scopes, try to acquire a valid token
    if OTHER_AUTH_SCOPES:
        logging.info("[webbackend] Attempting to acquire token for other scopes.")
        try:
            other_access_token = get_valid_access_token(OTHER_AUTH_SCOPES)
            session["other_access_token"] = other_access_token
        except Exception as ex:
            logging.warning(f"Could not acquire token for other scopes {OTHER_AUTH_SCOPES}. Error: {str(ex)}")
            return f"Other scopes token acquisition failure: {str(ex)}", 400

    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    if ENABLE_AUTHENTICATION:
        session.clear()
        # Redirect to Azure AD logout endpoint if desired
        return redirect(
            AUTHORITY + "/oauth2/v2.0/logout" +
            "?post_logout_redirect_uri=" + url_for("index", _external=True)
        )
    else:
        return redirect(url_for("index"))

# Helper functions for MSAL token cache management and building the MSAL app instance:
def _build_auth_url(scopes=None, state=None):
    return _build_msal_app().get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for("authorized", _external=True)
    )

def _build_msal_app(cache=None):
    return msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
        token_cache=cache
    )

def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

# --- End Authentication Endpoints ---

# Serve the main index page.
@app.route("/")
def index():
    if ENABLE_AUTHENTICATION and not session.get("user"):
        # If authentication is enabled and the user is not in the session,
        # redirect to the login endpoint.
        return redirect(url_for("login"))
    # Otherwise, serve the index.html page.
    return app.send_static_file("index.html")

# Serve all other static assets (e.g., JS, CSS, images)
@app.route("/<path:path>")
def static_files(path):
    return app.send_static_file(path)

def check_authorization():
    # If authentication is disabled, return a default authorized user.
    if not ENABLE_AUTHENTICATION:
        return {
            'authorized': True,
            'client_principal_id': 'no-auth',
            'client_principal_name': 'anonymous',
            'client_group_names': [],
            'access_token': None
        }
    
    # Expect that after a successful login, user info is stored in session.
    user = session.get("user")
    if not user:
        logging.info("[webbackend] No user in session; user is not authenticated.")
        return {
            'authorized': False,
            'client_principal_id': None,
            'client_principal_name': None,
            'client_group_names': [],
            'access_token': None
        }
    
    client_principal_id = user.get("oid")  # or another unique claim
    client_principal_name = user.get("preferred_username") or user.get("upn")
    
    # Refresh Graph access token for the current user
    try:
        graph_access_token = get_valid_access_token(SCOPE)
        session["graph_access_token"] = graph_access_token
    except Exception as ex:
        logging.error(f"[webbackend] Failed to refresh Graph token: {str(ex)}")
        graph_access_token = session.get("graph_access_token", None)
    
    # If additional scopes are configured, try to refresh them as well
    other_access_token = None
    if OTHER_AUTH_SCOPES:
        try:
            other_access_token = get_valid_access_token(OTHER_AUTH_SCOPES)
            session["other_access_token"] = other_access_token
        except Exception as ex:
            logging.error(f"[webbackend] Failed to refresh other scopes token: {str(ex)}")
            other_access_token = session.get("other_access_token", None)
    
    access_token = other_access_token if other_access_token else graph_access_token
    
    # Retrieve groups from Graph API using a valid Graph access token.
    groups = []
    if graph_access_token:
        try:
            graph_headers = {'Authorization': f'Bearer {graph_access_token}'}
            graph_url = 'https://graph.microsoft.com/v1.0/me/memberOf'
            graph_response = requests.get(graph_url, headers=graph_headers)
            graph_response.raise_for_status()
            group_data = graph_response.json()
            groups = [group.get('displayName', 'missing-group-read-all-permission') for group in group_data.get('value', [])]
            logging.info(f"[webbackend] User groups from Graph API: {groups}")
        except Exception as e:
            logging.info(f"[webbackend] Failed to get user groups from Graph API: {e}")
    else:
        logging.info("[webbackend] No valid Graph access token available; cannot get user groups")
    
    # Allowed users/groups logic
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
            logging.info("[webbackend] User is not in allowed groups or users.")
    
    return {
        'authorized': authorized,
        'client_principal_id': client_principal_id,
        'client_principal_name': client_principal_name,
        'client_group_names': groups,
        'access_token': access_token
    }

@app.route("/chatgpt", methods=["POST"])
def chatgpt():
    start_time = time.time()  # Start the timer    
    conversation_id = request.json["conversation_id"]
    question = request.json["query"]
    
    logging.info("[webbackend] conversation_id: " + conversation_id)    
    logging.info("[webbackend] question: " + question)
    
    # Check authorization (this will return dummy values if authentication is disabled)
    auth_info = check_authorization()
    
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
    access_token = auth_info['access_token']

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

        # Forward the access token if enabled and available.
        if FORWARD_ACCESS_TOKEN_TO_ORCHESTRATOR and access_token:
            logging.info("[webbackend] Forwarding access token to orchestrator.")
            payload['access_token'] = access_token

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
    logging.info(f"Starting getBlob function for blob: {blob_name}")
    try:
        client_credential = ChainedTokenCredential(
            ManagedIdentityCredential(),
            AzureCliCredential()
        )
        blob_service_client = BlobServiceClient(
            f"https://{STORAGE_ACCOUNT}.blob.core.windows.net",
            client_credential
        )
        blob_client = blob_service_client.get_blob_client(container='documents', blob=blob_name)
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