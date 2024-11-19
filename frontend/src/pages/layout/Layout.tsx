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
                        <img height="80px" src="https://news.microsoft.com/wp-content/uploads/prod/sites/113/2017/06/Microsoft-logo_rgb_c-gray.png"></img>
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
