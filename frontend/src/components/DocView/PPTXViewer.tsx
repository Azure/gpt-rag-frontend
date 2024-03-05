import React, { useState, useEffect } from "react";

interface PptxViewerProps {
    file: Blob;
}

const PptxViewer: React.FC<PptxViewerProps> = ({ file }) => {
    let url = URL.createObjectURL(file);

    useEffect(() => {}, []);

    return (
        <div>
            <iframe srcDoc={url}></iframe>
        </div>
    );
};

export default PptxViewer;
