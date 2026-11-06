# Changelog

## 0.0.1

- Require authenticated, authorized access to chat and data APIs by default.
- Use short-lived document read tokens bound to the user and session.
- Keep browser API calls same-origin and remove permissive cross-origin access.
- Return generic JSON errors for login failures and require callback state.
- Update document previews and development proxies for the read-token flow.
- Include offline regression coverage and authentication configuration guidance.
- Provide an application ZIP containing the backend and compiled frontend.

### Upgrade notes

Configure Entra authentication and Key Vault secrets before deployment. Setting
`ENABLE_AUTHENTICATION=false` no longer enables anonymous access to protected
routes. Deploy both application components together. Document integrations must
request a read token before downloading a document.
