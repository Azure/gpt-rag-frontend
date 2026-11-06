# GPT on your data Frontend

Part of [GPT-RAG](https://github.com/Azure/gpt-rag)

## Application releases

The `v0.0.1` release includes `gpt-rag-frontend-v0.0.1-app.zip`, containing the
backend runtime files and the compiled frontend. The ZIP has `app.py`,
`requirements.txt`, `.deployment`, and `static/` at its root. It does not include
local environment files, sessions, virtual environments, or development tools.
Use the accompanying `SHA256SUMS.txt` to verify the downloaded package.

Configure authentication and Key Vault secrets before deploying the package.
Deploy the frontend and backend together. Custom document clients must use the
read-token flow described below. Publishing a GitHub release does not update
existing Azure deployments.

## Authentication and document access

Authentication is enabled by default. Configure the Entra application client ID,
authority, registered redirect URI, and client secret before serving the app.
The Flask session secret and application client secret are read from Key Vault.
A missing Flask session secret prevents startup. Keep that secret private and
consistent across application instances.

All `/api/*` routes and `/chatgpt` require an authenticated user and apply the
same application authorization rules (`ALLOWED_GROUP_NAMES`,
`ALLOWED_USER_PRINCIPALS`, and `ALLOWED_USER_NAMES`). With no allowlist, any user
authenticated by the configured Entra application has application access.
`ALLOWED_USER_PRINCIPALS` is compared to the user's Entra object ID (`oid`).
Use `ALLOWED_USER_NAMES` for the `preferred_username` or `upn` claim.
Setting `ENABLE_AUTHENTICATION=false` does not expose data anonymously.
Protected routes return HTTP 503 until authentication is enabled again.
Unauthenticated requests return HTTP 401 and disallowed users receive HTTP 403.

The browser uses same-origin requests. The backend does not enable cross-origin
API access or reflect arbitrary origins. During Vite development, the proxy
forwards API and authentication routes to the backend without enabling CORS.
If you change `REDIRECT_PATH`, update the Vite callback proxy accordingly.
Open `/login` on the Vite origin before using the development UI.

Document previews use this authenticated, same-origin flow:

1. POST `{"blob_name": "report.pdf"}` to `/api/get-blob-token`.
2. POST the returned `{"token": "..."}` to `/api/get-blob`.

The signed read token expires after five minutes and is bound to the current
user, server-side session, and document in the fixed `documents` container.
Another session cannot reuse it, even for the same user. Logging out invalidates
that session's grants. The download endpoint no longer accepts a document name
without a token. Protected responses use `Cache-Control: no-store`.
Do not put read tokens in URLs or logs.

These are application-wide corpus permissions, not per-document ACLs. An
authorized application user can request a token for a document in that corpus.
Deployments needing document-level permissions must enforce those permissions
before issuing read tokens.

Session cookies are HTTP-only, SameSite=Lax, and secure by default.
Set `SESSION_COOKIE_SECURE=false` only when testing with local HTTP.
Rebuild and deploy the frontend and backend together because document previews
now use the token endpoint. Updating the source alone does not update existing
deployments.

### Offline regression tests

From the repository root, use a Python environment with the backend dependencies:

```text
python -m pip install -r backend/requirements.txt
python -m unittest discover -s backend/tests -v
```

The tests replace Key Vault, identity, Graph, Blob Storage, and orchestrator
interactions with local fixtures. They do not require Azure sign-in or resources.

## Deploy (quickstart)

**Pre-reqs**

- Zip command
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- Node.js 16+ [windows/mac](https://nodejs.dev/en/download/)  [linux/wsl](https://nodejs.dev/en/download/package-manager/)
- Install ZIP in WSL/Linux: sudo apt-get install zip

**1) Clone the Repository**

```
git clone https://github.com/Azure/gpt-rag-frontend.git
```

If you plan to customize the application code, create a new repo by clicking on the Use **this template** button on top of this page.

If you created a new repository please update the repository URL before running the git clone command

**2) Build App**

Everytime you change frontend code you need to build it before a new deployment, including in the first time:

```
cd frontend
npm install
npm run build
```

**3) Deploy to Azure** 

Execute the following commands in the terminal to deploy your function:

2.1. Enter backend folder
 
```
cd ..
cd backend
```

2.2. Remove backend_env if you have tested it locally

bash:
```
rm -rf backend_env  
```

or 

Powershell:
```
Remove-Item -Recurse -Force backend_env
```

2.3. Zip source code

Linux or Mac:
```
zip -r ../deploy.zip *
```

Windows:
```
tar -a -c -f ../deploy.zip *
```

2.4. Deploy it with az webapp deploy:

```
cd ..
az webapp deploy --subscription [SUBSCRIPTION_ID] --resource-group [RESOURCE_GROUP_NAME] --name [WEB_APP_NAME] --src-path deploy.zip --type zip --async true
```

## **(Optional) Test locally**  

Before running the application locally, make sure that the necessary Azure resources (like Blob Storage, AI services, and the Orchestrator) are already deployed in the cloud. Don’t worry—this can easily be done using `azd provision`, as outlined in the setup guide for the GPT-RAG repository.

1) Rename `.env.template` to `.env` and update the environment variables with your details.

2) Log in to your Azure account by running `azd auth login` or `az login`.

3) Start the application by running `./start.sh` (or `./startwin.sh` if you’re on Windows).

### Permissions for your user to run the frontend app locally

Assign the necessary permissions to the user who will run the frontend application locally. Below are the specific roles and the corresponding commands.

Replace the variables (those starting with the $ symbol) with the corresponding values from your deployment, keeping in mind that `principalId` is the identifier of your user in Entra ID.

- **Orchestrator**  
   Assign the "Contributor" role to the user for accessing function app.
   ```bash
    az role assignment create \
        --assignee $principalId \
        --role "Contributor" \
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Web/sites/$functionAppName"
   ```

- **Storage Account**  
   Assign the "Storage Blob Data Reader" role to the user for accessing blob storage.
   ```bash
   az role assignment create \
       --assignee $principalId \
       --role "Storage Blob Data Reader" \
       --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$storageAccountName"
   ```

- **Key Vault**  
   Assign the "Key Vault Secrets User" role to the user to access secrets.
   ```bash
   az role assignment create \
       --assignee $principalId \
       --role "Key Vault Secrets User" \
       --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.KeyVault/vaults/$keyVaultName"
   ```

- **Azure AI Services**  
   Assign the "Cognitive Services Contributor" role to the user for using AI services.
   ```bash
   az role assignment create \
       --assignee $principalId \
       --role "Cognitive Services Contributor" \
       --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.CognitiveServices/accounts/$aiServicesAccountName"
   ```

- **Application Insights**  
   Assign the "Application Insights Component Contributor" role to the user for monitoring.
   ```bash
   az role assignment create \
       --assignee $principalId \
       --role 'Application Insights Component Contributor' \
       --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/microsoft.insights/components/$appInsightsName"
   ```

## Frontend customizations

Optionally you can customize some items in the frontend.

**1) Title**

Update page's title

file: ```frontend/src/pages/layout/Layout.tsx```

```
<h4 className={styles.headerRightText}>Chat On Your Data/h4>
```

file: ```frontend/src/pages/layout/index.html```

```
<title>Chat Chat On Your Data | Demo</title>
```

**2) Logo**

Update frontend logo

file: ```frontend/src/pages/layout/Layout.tsx```

Example:
```
<Link to="/" className={styles.headerTitleContainer}>
    <img height="80px" src="https://www.yourdomain.com/yourlogo.png"></img>
    <h3 className={styles.headerTitle}></h3>
</Link>
```

**3) Citations**

You can remove citations from the answers if you do not want them. Just set showSources to {false}

file: ```frontend/src/pages/chat/Chat.tsx```

```
<Answer
    key={index}
    answer={answer[1]}
    isSelected={selectedAnswer === index && activeAnalysisPanelTab !== undefined}
    onCitationClicked={c => onShowCitation(c, index)}
    onThoughtProcessClicked={() => onToggleTab(AnalysisPanelTabs.ThoughtProcessTab, index)}
    onSupportingContentClicked={() => onToggleTab(AnalysisPanelTabs.SupportingContentTab, index)}
    onFollowupQuestionClicked={q => makeApiRequestGpt(q)}
    showFollowupQuestions={false}
    showSources={false}                                            
/>
```

**4) Speech Synthesis**

To enable speech synthesis change speechSynthesisEnabled variable to true.

file: ```frontend/src/pages/chat/Chat.tsx```

```
const speechSynthesisEnabled = true;
```

## Contributing

We appreciate your interest in contributing to this project! Please refer to the [CONTRIBUTING.md](https://github.com/Azure/GPT-RAG/blob/main/CONTRIBUTING.md) page for detailed guidelines on how to contribute, including information about the Contributor License Agreement (CLA), code of conduct, and the process for submitting pull requests.

Thank you for your support and contributions!

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
