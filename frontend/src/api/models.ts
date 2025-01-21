export const enum Approaches {
    RetrieveThenRead = "rtr",
    ReadRetrieveRead = "rrr",
    ReadDecomposeAsk = "rda"
}

export type AskRequestOverrides = {
    semanticRanker?: boolean;
    semanticCaptions?: boolean;
    excludeCategory?: string;
    top?: number;
    temperature?: number;
    promptTemplate?: string;
    promptTemplatePrefix?: string;
    promptTemplateSuffix?: string;
    suggestFollowupQuestions?: boolean;
};

export type AskRequest = {
    question: string;
    approach: Approaches;
    overrides?: AskRequestOverrides;
};

export interface Thought {
    speaker: string;
    message_type: string;
    content: string | string[];
}

export type AskResponse = {
    answer: string;
    thoughts: string | Thought[] | null;
    data_points: string[];
    error?: string;
};

export type TransactionData = {
    cuenta_origen: string;
    monto: string;
    telefono_destino: string;
}

export type AskResponseGpt= {
    conversation_id: string;
    answer: string;
    current_state: string;
    thoughts: string | Thought[] | null;
    data_points: string[];
    transaction_data?: TransactionData;
    error?: string;
};

export type ChatTurn = {
    user: string;
    bot?: string;
};

export type ChatRequest = {
    history: ChatTurn[];
    approach: Approaches;
    overrides?: AskRequestOverrides;
};

export type ChatRequestGpt = {
    history: ChatTurn[];
    approach: Approaches;
    conversation_id: string;
    query: string;
    overrides?: AskRequestOverrides;
};

