import { Outlet, Link } from "react-router-dom";

import styles from "./Layout.module.css";
import companyLogo from "../../assets/logo.svg";

const Layout = () => {
    const examples = [
        "Provide a summary of my contract in plain English",
        "What was our sales revenue last quarter?",
        "What is the sentiment of the customer reviews?",
    ];

    const showExamples = process.env.REACT_APP_UI_EXAMPLES;
    console.log("showExamples", showExamples);
    
    return (
        <div className={styles.layout}>
            <header className={styles.header} role={"banner"}>
                <div className={styles.headerContainer}>
                    <Link to="/" className={styles.headerTitleContainer}>
                        <img height="80px" src="data:image/png;base64,UklGRmgXAABXRUJQVlA4TFwXAAAv18fgEB9hEJKUdXmYZBOIKYwmBzNt27h/SZfyCIwgECSnSQabdQUDAVA0oSlZYLsHJnggCyQw71HozQEhEWBfAGOwKHRWwA+Lg686Q0gEyFHcto0j7b92rvd7RcQEgB8oo/UJ0IzZWztQzbNG1cB01iItzNIC7eJz93bbbt7Wtq1h7fd3URRJdPBt7///N/NiAaSYMb2ZsiL6PwEOIklSpGd+D+Tf6MVsH19G9H8C6O/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+53/+5/9t4M97mP/xyu8f5qrK/RXmf7/y+YbJf/zHf/zHf/zHf/zHf/zHf/zHf3/3H//xH//xH//xH//xn2vEELz7PIQQf4WL51EFr0vtZ/jFLZ0NuvXk39jSWWAw/L4WGmz+uhYqrP6yFivs/qrGByz/phYy9k8cQng/OmB8P8S+F3xe+sXvQ1ywd0pd8H3p6U0oCrZO7HDnwe9AUbCt4GD7SThY1osZ95b4/hME+4oA2+lBDlhW84K7Jbz7RME25HgQmYiHZnjviYJ9iDyHxzwCVCW+8yTBRgTXY9R5JNFB5vcdLtiKtKeImEeF9vG+07EXQXqIPo8A/fSu47Ebcc/AMo9qoL/pJNmO5GfwmEaERX7PqdiOIDxCmYcz4d9yLmxI+hMEzKOa6G85eUcCfoA+EZgs7zgOWxI/P8Y82AbecFj2JGV+50TCu5KH1XJckT4P11Gs8ZV2C4jTy+9v2YYciV5lX+ykswFhu9BnF/D2FmDyYLo1HWIhuoKP+wWZXZtJelPqFiTQ7cxaV8/4cr8AP7eEmZCN/H4jBgrTmOyb4Lsbhjo3N5dior3dXNAvTCOms+DVDQPS1PJcDhPn203Xk0j2w5Fx447hmNmFuVwm0ttN1jvJOF9dcO+OIc+sToaygUrvtgnq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"></img>
                        <h3 className={styles.headerTitle}></h3>
                    </Link>
                    <nav>
                    </nav>
                    <h4 className={styles.headerRightText}>Chat On Your Data</h4>
                </div>
            </header>
            {/* Main content starts here */}
            {showExamples && (
                <main className={styles.mainContent}>
                    <div className={styles.logoContainer}>
                        <img
                            src={companyLogo}
                            alt="Company Logo"
                            className={styles.companyLogo}
                        />
                    </div>
                    <div className={styles.examplesSection}>
                        <h2>Examples</h2>
                        <div className={styles.examplesGrid}>
                            {examples.map((example, index) => (
                                <div key={index} className={styles.exampleBubble}>
                                    <p className={styles.exampleText}>{example}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </main>
            )}
            <Outlet />
        </div>
    );
};

export default Layout;
