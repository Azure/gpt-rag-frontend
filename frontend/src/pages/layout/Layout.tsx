import { Outlet, Link } from "react-router-dom";

import styles from "./Layout.module.css";

const Layout = () => {
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

            <Outlet />
        </div>
    );
};

export default Layout;
