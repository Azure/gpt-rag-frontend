import importlib.util
import os
from pathlib import Path
import socket
import sys
import tempfile
import time
import types
import unittest
from unittest.mock import Mock, patch

from azure.core.exceptions import AzureError, ResourceNotFoundError
from flask_session import Session


class ApiAuthorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session_dir = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.session_dir.cleanup)
        keyvault = types.ModuleType("keyvault")
        keyvault.get_secret = Mock(return_value="local-test-session-secret-not-for-deployment")

        def configure_session(app):
            app.config["SESSION_FILE_DIR"] = cls.session_dir.name
            return Session(app)

        spec = importlib.util.spec_from_file_location(
            "frontend_security_app", Path(__file__).resolve().parents[1] / "app.py"
        )
        cls.module = importlib.util.module_from_spec(spec)
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.dict(sys.modules, {"keyvault": keyvault, spec.name: cls.module}),
            patch("dotenv.load_dotenv"),
            patch("flask_session.Session", side_effect=configure_session),
            patch.object(socket.socket, "connect", side_effect=AssertionError("Network access forbidden")),
        ):
            spec.loader.exec_module(cls.module)
        cls.authentication_default = cls.module.ENABLE_AUTHENTICATION
        cls.module.app.config["TESTING"] = True

    def setUp(self):
        self.client = self.module.app.test_client()
        self.connect = self.patch(
            socket.socket, "connect", side_effect=AssertionError("Network access forbidden")
        )
        self.patch(self.module, "ENABLE_AUTHENTICATION", True)
        self.patch(self.module, "ALLOWED_GROUP_NAMES", [])
        self.patch(self.module, "ALLOWED_USER_PRINCIPALS", [])
        self.patch(self.module, "ALLOWED_USER_NAMES", [])
        self.patch(self.module, "OTHER_AUTH_SCOPES", [])
        self.patch(self.module, "STORAGE_ACCOUNT", "teststorage")
        self.patch(self.module, "get_valid_access_token", return_value="local-graph-fixture")
        self.managed_token = self.patch(
            self.module, "get_managed_identity_token", return_value="local-managed-fixture"
        )
        self.function_key = self.patch(
            self.module, "get_function_key", return_value="local-function-fixture"
        )
        self.credentials = self.patch(self.module, "ChainedTokenCredential")
        self.patch(self.module, "ManagedIdentityCredential")
        self.patch(self.module, "AzureCliCredential")
        self.storage = self.patch(self.module, "BlobServiceClient")
        self.storage.return_value.get_blob_client.return_value.download_blob.return_value.readall.return_value = b"private fixture"
        self.graph = self.patch(self.module.requests, "get")
        self.graph.return_value.json.return_value = {"value": [{"displayName": "employees"}]}
        self.upstream = self.patch(self.module.requests, "post")
        self.upstream.return_value.text = '{"answer":"fixture answer","conversation_id":"fixture-conversation"}'

    def patch(self, target, attribute, *args, **kwargs):
        patcher = patch.object(target, attribute, *args, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def authenticate(self, client=None, principal="user-a"):
        client = client or self.client
        with client.session_transaction(base_url="https://frontend.example.test") as session:
            session["user"] = {"oid": principal, "preferred_username": f"{principal}@example.test"}

    def request(self, method, path, client=None, **kwargs):
        return (client or self.client).open(
            path, method=method, base_url="https://frontend.example.test", **kwargs
        )

    def authorize_callback(self, **query):
        with self.client.session_transaction(base_url="https://frontend.example.test") as session:
            session["state"] = "callback-fixture"
        return self.request("GET", self.module.REDIRECT_PATH, query_string={
            "state": "callback-fixture", **query
        })

    def grant(self, name="report.pdf", client=None):
        response = self.request("POST", "/api/get-blob-token", client, json={"blob_name": name})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["expires_in"], 300)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        return response.json["token"]

    def assert_no_resource_access(self):
        self.storage.assert_not_called()
        self.credentials.assert_not_called()
        self.managed_token.assert_not_called()
        self.function_key.assert_not_called()
        self.upstream.assert_not_called()
        self.connect.assert_not_called()

    def test_authentication_and_secure_cookie_defaults(self):
        self.assertTrue(self.authentication_default)
        self.assertTrue(self.module.app.config["SESSION_COOKIE_SECURE"])
        self.assertTrue(self.module.app.config["SESSION_COOKIE_HTTPONLY"])
        self.assertEqual(self.module.app.config["SESSION_COOKIE_SAMESITE"], "Lax")
        self.assertTrue(self.module.app.config["SESSION_USE_SIGNER"])

    def test_every_data_route_denies_anonymous_requests_before_resource_access(self):
        routes = [
            ("POST", "/chatgpt"),
            ("POST", "/api/get-blob"),
            ("POST", "/api/get-blob-token"),
            ("GET", "/api/get-speech-token"),
            ("GET", "/api/get-storage-account"),
            ("GET", "/api/future-data-route"),
        ]
        for method, path in routes:
            with self.subTest(path=path):
                response = self.request(method, path, json={})
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assert_no_resource_access()

    def test_disabled_authentication_never_enables_anonymous_data_access(self):
        self.module.ENABLE_AUTHENTICATION = False
        for method, path in [
            ("POST", "/chatgpt"),
            ("POST", "/api/get-blob"),
            ("POST", "/api/get-blob-token"),
            ("GET", "/api/get-speech-token"),
            ("GET", "/api/get-storage-account"),
        ]:
            with self.subTest(path=path):
                self.assertEqual(self.request(method, path, json={}).status_code, 503)
        self.assert_no_resource_access()

    def test_authenticated_but_disallowed_user_is_denied_on_every_data_route(self):
        self.authenticate()
        self.module.ALLOWED_USER_PRINCIPALS = ["different-user"]
        for method, path in [
            ("POST", "/chatgpt"),
            ("POST", "/api/get-blob"),
            ("POST", "/api/get-blob-token"),
            ("GET", "/api/get-speech-token"),
            ("GET", "/api/get-storage-account"),
        ]:
            with self.subTest(path=path):
                self.assertEqual(self.request(method, path, json={}).status_code, 403)
        self.assert_no_resource_access()

    def test_allowed_user_and_group_configuration_still_works(self):
        self.authenticate()
        for setting, allowed in [
            ("ALLOWED_USER_PRINCIPALS", "user-a"),
            ("ALLOWED_USER_NAMES", "user-a@example.test"),
            ("ALLOWED_GROUP_NAMES", "employees"),
        ]:
            with self.subTest(setting=setting), patch.object(self.module, setting, [allowed]):
                response = self.request("GET", "/api/get-storage-account")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_json(force=True), {"storageaccount": "teststorage"})

    def test_session_without_user_object_id_is_denied(self):
        with self.client.session_transaction(base_url="https://frontend.example.test") as session:
            session["user"] = {"preferred_username": "user-a@example.test"}
        self.assertEqual(self.request("GET", "/api/get-storage-account").status_code, 403)
        self.assert_no_resource_access()

    def test_cors_preflights_do_not_reflect_untrusted_origins(self):
        for path in ["/api/get-blob", "/api/get-blob-token", "/chatgpt"]:
            with self.subTest(path=path):
                response = self.request("OPTIONS", path, headers={
                    "Origin": "https://untrusted.example",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type",
                })
                self.assertNotIn("Access-Control-Allow-Origin", response.headers)
                self.assertNotIn("Access-Control-Allow-Credentials", response.headers)
        self.assert_no_resource_access()

    def test_denial_responses_also_do_not_enable_cors(self):
        response = self.request("POST", "/api/get-blob", json={}, headers={
            "Origin": "https://untrusted.example"
        })
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("Access-Control-Allow-Origin", response.headers)

    def test_document_download_uses_granted_name_in_fixed_container(self):
        self.authenticate()
        token = self.grant("folder/report.pdf")
        response = self.request("POST", "/api/get-blob", json={
            "token": token, "blob_name": "different-private-document.pdf"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"private fixture")
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.storage.return_value.get_blob_client.assert_called_once_with(
            container="documents", blob="folder/report.pdf"
        )

    def test_document_name_alone_cannot_download_data(self):
        self.authenticate()
        response = self.request("POST", "/api/get-blob", json={"blob_name": "report.pdf"})
        self.assertEqual(response.status_code, 400)
        self.assert_no_resource_access()

    def test_tampered_token_cannot_download_data(self):
        self.authenticate()
        token = self.grant()
        response = self.request("POST", "/api/get-blob", json={"token": "tampered-" + token})
        self.assertEqual(response.status_code, 403)
        self.assert_no_resource_access()

    def test_expired_token_cannot_download_data(self):
        self.authenticate()
        signer = type(self.module.document_tokens.make_signer())
        with patch.object(signer, "get_timestamp", return_value=int(time.time()) - 301):
            token = self.grant()
        response = self.request("POST", "/api/get-blob", json={"token": token})
        self.assertEqual(response.status_code, 403)
        self.assertIn("expired", response.json["error"])
        self.assert_no_resource_access()

    def test_token_is_valid_at_five_minute_boundary(self):
        self.authenticate()
        timestamp = int(time.time())
        signer = type(self.module.document_tokens.make_signer())
        with patch.object(signer, "get_timestamp", return_value=timestamp):
            token = self.grant()
        with patch.object(signer, "get_timestamp", return_value=timestamp + 300):
            response = self.request("POST", "/api/get-blob", json={"token": token})
        self.assertEqual(response.status_code, 200)

    def test_different_session_cannot_reuse_same_users_token(self):
        self.authenticate()
        token = self.grant()
        second_client = self.module.app.test_client()
        self.authenticate(second_client)
        self.grant(client=second_client)
        response = self.request("POST", "/api/get-blob", second_client, json={"token": token})
        self.assertEqual(response.status_code, 403)
        self.assert_no_resource_access()

    def test_different_user_cannot_reuse_token_in_same_session(self):
        self.authenticate()
        token = self.grant()
        self.authenticate(principal="user-b")
        response = self.request("POST", "/api/get-blob", json={"token": token})
        self.assertEqual(response.status_code, 403)
        self.assert_no_resource_access()

    def test_logout_invalidates_tokens_even_after_signing_in_again(self):
        self.authenticate()
        token = self.grant()
        self.assertEqual(self.request("GET", "/logout").status_code, 302)
        self.assertEqual(self.request("POST", "/api/get-blob", json={"token": token}).status_code, 401)
        self.authenticate()
        self.assertEqual(self.request("POST", "/api/get-blob", json={"token": token}).status_code, 403)
        self.assert_no_resource_access()

    def test_changed_allowlist_revokes_existing_token_access(self):
        self.authenticate()
        token = self.grant()
        self.module.ALLOWED_USER_PRINCIPALS = ["different-user"]
        self.assertEqual(self.request("POST", "/api/get-blob", json={"token": token}).status_code, 403)
        self.assert_no_resource_access()

    def test_invalid_document_names_are_rejected(self):
        self.authenticate()
        for name in [None, 42, "", " ", "../report.pdf", "%2E%2E/report.pdf",
                     "/report.pdf", "folder\\report.pdf", "report\x00.pdf", "a" * 1025]:
            with self.subTest(name=name):
                response = self.request("POST", "/api/get-blob-token", json={"blob_name": name})
                self.assertEqual(response.status_code, 400)
        self.assert_no_resource_access()

    def test_bad_request_shapes_are_rejected(self):
        self.authenticate()
        for path in ["/api/get-blob", "/api/get-blob-token", "/chatgpt"]:
            for body in [[], "text", 42, None, {}]:
                with self.subTest(path=path, body=body):
                    response = self.request("POST", path, json=body)
                    self.assertEqual(response.status_code, 400)
        self.assert_no_resource_access()

    def test_storage_errors_do_not_disclose_internal_details(self):
        self.authenticate()
        token = self.grant()
        self.storage.return_value.get_blob_client.side_effect = AzureError("private infrastructure details")
        response = self.request("POST", "/api/get-blob", json={"token": token})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private infrastructure", response.get_data(as_text=True))

    def test_missing_document_has_explicit_not_found_response(self):
        self.authenticate()
        token = self.grant()
        self.storage.return_value.get_blob_client.side_effect = ResourceNotFoundError("missing fixture")
        self.assertEqual(self.request("POST", "/api/get-blob", json={"token": token}).status_code, 404)

    def test_authenticated_chat_preserves_response_and_user_identity(self):
        self.authenticate()
        response = self.request("POST", "/chatgpt", json={
            "query": "hello", "conversation_id": "", "client_principal_id": "different-user"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(force=True)["answer"], "fixture answer")
        payload = self.upstream.call_args.kwargs["json"]
        self.assertEqual(payload["client_principal_id"], "user-a")
        self.assertEqual(payload["client_principal_name"], "user-a@example.test")
        self.graph.assert_called_once()

    def test_authenticated_speech_token_still_works(self):
        self.authenticate()
        self.upstream.return_value.text = "speech-token-fixture"
        response = self.request("GET", "/api/get-speech-token")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(force=True)["token"], "speech-token-fixture")
        self.managed_token.assert_called_once()

    def test_login_redirect_stays_available_without_authentication(self):
        self.assertEqual(self.request("GET", "/").status_code, 302)
        self.assert_no_resource_access()

    def test_login_callback_requires_matching_nonempty_state(self):
        msal_app = self.patch(self.module, "_build_msal_app")
        for query in [{}, {"state": ""}, {"state": "different-state"}]:
            with self.subTest(query=query):
                response = self.request("GET", self.module.REDIRECT_PATH, query_string={
                    **query, "code": "fixture-code"
                })
                self.assertEqual(response.status_code, 302)
        msal_app.assert_not_called()
        self.assert_no_resource_access()

    def test_login_callback_error_does_not_reflect_html(self):
        description = '<script>alert("fixture")</script>'
        response = self.authorize_callback(error="access_denied", error_description=description)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.json, {"error": "Authentication failed."})
        self.assertNotIn(description, response.get_data(as_text=True))
        self.assert_no_resource_access()

    def test_login_token_error_does_not_disclose_provider_details(self):
        description = '<script>alert("provider fixture")</script>'
        msal_app = self.patch(self.module, "_build_msal_app")
        msal_app.return_value.acquire_token_by_authorization_code.return_value = {
            "error": "invalid_grant", "error_description": description
        }
        response = self.authorize_callback(code="fixture-code")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.json, {"error": "Authentication failed."})
        self.assertNotIn(description, response.get_data(as_text=True))
        self.assert_no_resource_access()

    def test_other_scope_error_does_not_disclose_exception_details(self):
        description = '<script>alert("scope fixture")</script>'
        self.module.OTHER_AUTH_SCOPES = ["api://fixture/scope"]
        self.patch(self.module, "get_valid_access_token", side_effect=Exception(description))
        msal_app = self.patch(self.module, "_build_msal_app")
        msal_app.return_value.acquire_token_by_authorization_code.return_value = {
            "id_token_claims": {"oid": "user-a"}, "access_token": "local-auth-fixture"
        }
        response = self.authorize_callback(code="fixture-code")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.json, {
            "error": "Could not acquire a token for the requested scopes."
        })
        self.assertNotIn(description, response.get_data(as_text=True))
        self.assert_no_resource_access()


if __name__ == "__main__":
    unittest.main()
