import React, { useState, useEffect } from "react";
import DOMPurify from "dompurify";
import mammoth from "mammoth";

interface DocxViewerProps {
    file: Blob;
}

const DocxViewer: React.FC<DocxViewerProps> = ({ file }) => {
    const [htmlContent, setHtmlContent] = useState<string>("");

    useEffect(() => {
        const reader = new FileReader();
        reader.onload = async () => {
            const arrayBuffer = reader.result as ArrayBuffer;
            const result = await mammoth.convertToHtml({ arrayBuffer });
            const sanitizedHtml = DOMPurify.sanitize(result.value);
            setHtmlContent(sanitizedHtml);
        };
        reader.readAsArrayBuffer(file);
    }, [file]);

    return <div dangerouslySetInnerHTML={{ __html: htmlContent }} />;
};

export default DocxViewer;
