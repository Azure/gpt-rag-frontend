import React, { useState, useEffect } from "react";

interface TextViewerProps {
    file: File | null;
}

const TextViewer: React.FC<TextViewerProps> = ({ file }) => {
    const [text, setText] = useState<string>("");

    useEffect(() => {
        if (!file) return; // Ensure file is defined before proceeding

        const reader = new FileReader();
        reader.onload = () => {
            const content = reader.result as string;
            // Escape < and > characters to prevent HTML interpretation
            const escapedContent = content
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;");
            setText(escapedContent);
        };
        reader.readAsText(file);
    }, [file]);

    return (
        <div style={{ width: "100%", maxWidth: "100%", overflowX: "auto", overflowY: "auto", whiteSpace: "pre-wrap" }}>
            <pre dangerouslySetInnerHTML={{ __html: text }}></pre>
        </div>
    );
};

export default TextViewer;
