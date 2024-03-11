import React, { useState, useEffect } from "react";

interface TextViewerProps {
    file: Blob;
}

const TextViewer: React.FC<TextViewerProps> = ({ file }) => {
    const [text, setText] = useState<string>("");

    useEffect(() => {
        const reader = new FileReader();
        reader.onload = () => {
            const content = reader.result as string;
            setText(content);
        };
        reader.readAsText(file);
    }, [file]);

    return (
        <div style={{ width: "100%", maxWidth: "100%", overflowX: "auto", overflowY: "auto", whiteSpace: "pre-wrap" }}>
            <pre>{text}</pre>
        </div>
    );
};

export default TextViewer;
