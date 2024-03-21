import { Toggle } from "@fluentui/react";

interface SwitchProps {
    useGPT4: boolean;
    toggle: () => void;
}
import styles from "./switchButton.module.css";

const SwitchButton = ({ useGPT4, toggle }: SwitchProps) => {
    return (
        <div className={styles.container}>
            <label className={styles.commandsContainer}>Usar GPT-4</label>
            <Toggle checked={useGPT4} onChange={toggle} className={styles.commandButton} />
        </div>
    );
};
export default SwitchButton;
