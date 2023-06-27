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


## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.

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