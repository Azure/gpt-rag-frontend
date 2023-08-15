import { Stack } from "@fluentui/react";
import { animated, useSpring } from "@react-spring/web";

import styles from "./Answer.module.css";
import { AnswerIcon } from "./AnswerIcon";

const userLanguage = navigator.language;
let gerando_resposta_text = '';
if (userLanguage.startsWith('pt')) {
  gerando_resposta_text = 'Gerando resposta';
} else if (userLanguage.startsWith('es')) {
  gerando_resposta_text = 'Generando respuesta';
} else {
  gerando_resposta_text = 'Generating response';
}

export const AnswerLoading = () => {
    const animatedStyles = useSpring({
        from: { opacity: 0 },
        to: { opacity: 1 }
    });

    return (
        <animated.div style={{ ...animatedStyles }}>
            <Stack className={styles.answerContainer} verticalAlign="space-between">
                <AnswerIcon />
                <Stack.Item grow>
                    <p className={styles.answerText}>
                        {gerando_resposta_text}
                        <span className={styles.loadingdots} />
                    </p>
                </Stack.Item>
            </Stack>
        </animated.div>
    );
};
