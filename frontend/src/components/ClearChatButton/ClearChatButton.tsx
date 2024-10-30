import { Text } from "@fluentui/react";
import { Delete24Regular } from "@fluentui/react-icons";

import styles from "./ClearChatButton.module.css";

import { getLanguageText } from '../../utils/languageUtils'; 

interface Props {
    className?: string;
    onClick: () => void;
    disabled?: boolean;
}

const reiniciar_text = getLanguageText('restartConversation');

export const ClearChatButton = ({ className, disabled, onClick }: Props) => {
    return (
        <div className={`${styles.container} ${className ?? ""} ${disabled && styles.disabled}`} onClick={onClick}>
            <Delete24Regular />
            <Text>{reiniciar_text}</Text>
        </div>
    );
};
