import { AskRequest, AskResponse, AskResponseGpt, ChatRequest, ChatRequestGpt } from "./models";



export async function chatApiGpt(options: ChatRequestGpt): Promise<AskResponseGpt> {
    const response = await fetch("/chatgpt", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            history: options.history,
            approach: options.approach,
            conversation_id: options.conversation_id,
            query: options.query,
            overrides: {
                semantic_ranker: options.overrides?.semanticRanker,
                semantic_captions: options.overrides?.semanticCaptions,
                top: options.overrides?.top,
                temperature: options.overrides?.temperature,
                prompt_template: options.overrides?.promptTemplate,
                prompt_template_prefix: options.overrides?.promptTemplatePrefix,
                prompt_template_suffix: options.overrides?.promptTemplateSuffix,
                exclude_category: options.overrides?.excludeCategory,
                suggest_followup_questions: options.overrides?.suggestFollowupQuestions
            }
        })
    });

    const parsedResponse: AskResponseGpt = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }

    return parsedResponse;
}

export function getCitationFilePath(citation: string): string {
    var storage_account = "please_check_if_storage_account_is_in_frontend_app_settings";
    
    const xhr = new XMLHttpRequest();
    xhr.open("GET", "/api/get-storage-account", false);
    xhr.send();

    if (xhr.status > 299) {
        console.log("Please check if STORAGE_ACCOUNT is in frontend app settings");
        return storage_account
    } else {
        const parsedResponse = JSON.parse(xhr.responseText);
        storage_account = parsedResponse['storageaccount'];
    }
    const file_path = `https://${storage_account}.blob.core.windows.net/documents/${citation}`
    console.log('Citation file path:' + file_path);
    return `https://${storage_account}.blob.core.windows.net/documents/${citation}`;
}