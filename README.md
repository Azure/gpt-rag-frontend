# gpt on your data frontend

## Quickstart - Deploy Frontend Web App

**1) Pre-reqs**

- Orchestrator deployed: [Orchestrator](https://github.com/placerda/gpt-oyd-orchestrator).
- Web App (App Service) with Python 3.10 runtime.
- Azure Speech Service.

**2) Set Startup Command**

In Azure Portal > Web App > Configuration > General Settings > Startup Command add:

```python ./app.py```

**3) Set Application Settings**

In Azure Portal > Web App > Configuration > Application Settings:

Add the application settings listed on [.env.template](.env.template), adjusting values accordingly to your environment.

**4) Build App**

Everytime you change frontend code you need to build it before a new deployment:

```
cd frontend
npm install
npm run build
```

**5) Deploy to Azure** 

In VSCode with [Azure Web App Extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azureappservice) go to the *Azure* Window, reveal your Web App in the resource explorer, right-click it then select *Deploy to Web App*.

**6) Deploy locally - Optional**

```
./start.sh
```

## Frontend customizations

**1) Blob storage path**

Update the blob storage path in the getCitationFilePath function to point to where your data is.

file: ```frontend/src/api/api.ts```

Example: storage account ```177960botistorage``` and storage container ```documents```
```
export function getCitationFilePath(citation: string): string {
    return `https://177960botistorage.blob.core.windows.net/documents/${citation}`;
}
```

**2) Title**

Update page's title

file: ```frontend/src/pages/layout/Layout.tsx```

```
<h4 className={styles.headerRightText}>Chat On Your Data/h4>
```

file: ```frontend/src/pages/layout/index.html```

```
<title>Chat Chat On Your Data | Demo</title>
```

**3) Logo**

Update frontend logo

file: ```frontend/src/pages/layout/Layout.tsx```

Example:
```
<Link to="/" className={styles.headerTitleContainer}>
    <img height="80px" src="https://www.yourdomain.com/yourlogo.png"></img>
    <h3 className={styles.headerTitle}></h3>
</Link>
```

**4) Home page text**

file: ```frontend/src/pages/chat/Chat.tsx```
```
                    <div className={styles.chatInput}>
                        <QuestionInput
                            clearOnSend
                            placeholder="Escriba aquí su pregunta"
                            disabled={isLoading}
                            onSend={question => makeApiRequestGpt(question)}
                        />
                    </div>
```

file: ```frontend/src/components/ClearChatButton.tsx```
```
        <div className={`${styles.container} ${className ?? ""} ${disabled && styles.disabled}`} onClick={onClick}>
            <Delete24Regular />
            <Text>{"Reiniciar conversación"}</Text>
        </div>
```

**5) Speech Synthesis**

To enable speech synthesis change speechSynthesisEnabled variable to true.

file: ```frontend/src/pages/chat/Chat.tsx```

```
const speechSynthesisEnabled = true;
```