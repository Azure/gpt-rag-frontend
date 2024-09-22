// frontend/src/components/DocView/XlsxViewer.tsx
import React from "react";

interface XlsxViewerProps {
    file: Blob;
    fileName?: string;
}

const XlsxViewer: React.FC<XlsxViewerProps> = ({ file, fileName = "file.xlsx" }) => {
    const url = URL.createObjectURL(file);

    return (
        <div style={{ textAlign: "left", padding: "20px" }}>
            <p style={{ textAlign: "left" }}>The XLSX file cannot be displayed in the browser. Please click the button below to download and view it.</p>
            <a href={url} download={fileName} style={{ textDecoration: "none" }}>
                <button style={{ padding: "10px 20px", fontSize: "16px", cursor: "pointer", backgroundColor: "#E6E8FF", color: "black", border: "none", borderRadius: "5px" }}>
                    Download
                </button>
            </a>
        </div>
    );
};

export default XlsxViewer;
