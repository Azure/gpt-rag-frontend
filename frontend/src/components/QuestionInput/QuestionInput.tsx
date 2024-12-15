import { useState } from "react";
import { Stack, TextField } from "@fluentui/react";
import { getTokenOrRefresh } from './token_util';
import { Send28Filled, BookOpenMicrophone28Filled, SlideMicrophone32Filled, AttachFilled } from "@fluentui/react-icons";
import { ResultReason, SpeechConfig, AudioConfig, SpeechRecognizer } from 'microsoft-cognitiveservices-speech-sdk';
import { getLanguageText } from '../../utils/languageUtils'; 

import styles from "./QuestionInput.module.css";

interface Props {
    onSend: (question: string, file?: File) => void;
    disabled: boolean;
    placeholder?: string;
    clearOnSend?: boolean;
}

export const QuestionInput = ({ onSend, disabled, placeholder, clearOnSend }: Props) => {
    const [question, setQuestion] = useState<string>("");
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const sendQuestion = () => {
        if (disabled || !question.trim()) {
            return;
        }

        onSend(question, selectedFile || undefined);

        if (clearOnSend) {
            setQuestion("");
            setSelectedFile(null);
        }
    };

    const sttFromMic = async () => {
        const tokenObj = await getTokenOrRefresh();
        const speechConfig = SpeechConfig.fromAuthorizationToken(tokenObj.authToken, tokenObj.region);
        speechConfig.speechRecognitionLanguage = tokenObj.speechRecognitionLanguage;
        
        const audioConfig = AudioConfig.fromDefaultMicrophoneInput();
        const recognizer = new SpeechRecognizer(speechConfig, audioConfig);

        const reiniciar_text = getLanguageText('micPrompt');

        setQuestion(reiniciar_text);

        recognizer.recognizeOnceAsync(result => {
            let displayText;
            if (result.reason === ResultReason.RecognizedSpeech) {
                displayText = result.text;
            } else {
                displayText = 'ERROR: Voice recognition was canceled or the voice cannot be recognized. Make sure your microphone is working properly.';
            }
            setQuestion(displayText);
        });
    };

    const onEnterPress = (ev: React.KeyboardEvent<Element>) => {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            sendQuestion();
        }
    };

    const onQuestionChange = (_ev: React.FormEvent<HTMLInputElement | HTMLTextAreaElement>, newValue?: string) => {
        if (!newValue) {
            setQuestion("");
        } else if (newValue.length <= 1000) {
            setQuestion(newValue);
        }
    };

    const onFileChange = (ev: React.ChangeEvent<HTMLInputElement>) => {
        if (ev.target.files && ev.target.files.length > 0) {
            setSelectedFile(ev.target.files[0]);
        }
    };

    const sendQuestionDisabled = disabled || !question.trim();

    return (
        <Stack horizontal className={styles.questionInputContainer}>
            <TextField
                className={styles.questionInputTextArea}
                placeholder={placeholder}
                multiline
                resizable={false}
                borderless
                value={question}
                onChange={onQuestionChange}
                onKeyDown={onEnterPress}
            />
            <div className={styles.questionInputButtonsContainer}>
                <div
                    className={`${styles.questionInputSendButton} ${sendQuestionDisabled ? styles.questionInputSendButtonDisabled : ""}`}
                    aria-label="Ask Questions"
                    onClick={sendQuestion}
                >
                    <Send28Filled primaryFill="rgba(115, 118, 225, 1)" />
                </div>
                <div
                    className={`${styles.questionInputSendButton}}`}
                    aria-label="Talk"
                    onClick={sttFromMic}
                >
                    <SlideMicrophone32Filled primaryFill="rgba(115, 118, 225, 1)" />
                </div>
                <label htmlFor="file-upload" className={styles.questionInputFileButton}>
                    <AttachFilled primaryFill="rgba(115, 118, 225, 1)" />
                </label>
                <input
                    id="file-upload"
                    type="file"
                    style={{ display: "none" }}
                    onChange={onFileChange}
                    disabled={disabled}
                />
            </div>
        </Stack>
    );
};
