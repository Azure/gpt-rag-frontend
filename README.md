# GPT on your data Frontend

Part of [GPT-RAG](https://github.com/Azure/gpt-rag)

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

If you plan to customize the ingestion logic, create a new repo by clicking on the Use **this template** button on top of this page.

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

```
rm -rf backend_env  
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

1) rename ```.env.template``` to ```.env``` updating the variables accordingly.

2) run ```azd auth login``` or ```az login```

3) run ```./start.sh```

## Frontend customizations

Optionally you can customize some itens in the frontend.

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
