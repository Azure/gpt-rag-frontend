import React, { useState, useEffect } from "react";
import FileViewer from "./FileViewer";

interface LazyDocViewerProps {
    base64Doc: string | undefined;
    page?: number | undefined;
    fileType: string;
    fileName?: string;
}

const DocView: React.FC<LazyDocViewerProps> = ({ base64Doc, page, fileType, fileName }) => {
    const [currentPage, setCurrentPage] = useState<number | undefined>(page);

    useEffect(() => {
        setCurrentPage(page);
    }, [base64Doc]);

    const base64toBlob = (data: string | undefined) => {
        if (data === undefined) {
            return "";
        }
        const base64WithoutPrefix = data.substr(data.indexOf(",") + 1);

        const bytes = atob(base64WithoutPrefix);
        let length = bytes.length;
        let out = new Uint8Array(length);

        while (length--) {
            out[length] = bytes.charCodeAt(length);
        }

        return new Blob([out], { type: fileType });
    };

    const blob = base64toBlob(base64Doc);

    return (
        <div>
            {base64Doc ? (
                <>
                    <FileViewer file={blob} fileType={fileType} page={currentPage} fileName={fileName} />
                </>
            ) : (
                <div>Loading Document...</div>
            )}
        </div>
    );
};

export default DocView;
