// src/utils/languageUtils.ts

type LanguageKey = 'restartConversation' | 'citationLabel' | 'generatingResponse' | 'micPrompt' | 'errorMessage';

const languageMap: Record<string, Record<LanguageKey, string>> = {
  en: {
    restartConversation: 'Restart conversation',
    citationLabel: 'Sources',
    generatingResponse: 'Generating response',
    micPrompt: 'You can talk using your microphone...',
    errorMessage: "I'm sorry, I had a problem with the request. Please report the error to the support team."
  },
  pt: {
    restartConversation: 'Reiniciar conversa',
    citationLabel: 'Fontes',
    generatingResponse: 'Gerando resposta',
    micPrompt: 'Pode falar usando seu microfone...',
    errorMessage: "Desculpe, tive um problema técnico com a solicitação. Por favor informar o erro à equipe de suporte."
  },
  es: {
    restartConversation: 'Reiniciar conversación',
    citationLabel: 'Fuentes',
    generatingResponse: 'Generando respuesta',
    micPrompt: 'Puedes hablar usando su micrófono...',
    errorMessage: "Lo siento, tuve un problema con la solicitud. Por favor informe el error al equipo de soporte."
  }
};

// Helper function to detect the user's language and return the correct text
export function getLanguageText(key: LanguageKey): string {
  const userLanguage = navigator.language;
  const lang = userLanguage.startsWith('pt') ? 'pt' : userLanguage.startsWith('es') ? 'es' : 'en';
  
  return languageMap[lang][key];
}

