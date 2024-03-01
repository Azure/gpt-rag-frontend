import React from "react";
import FileViewer from "offices-viewer";

interface PptxViewerProps {
    file: Blob;
    fileType: string;
}

const PptxViewer: React.FC<PptxViewerProps> = ({ file, fileType }) => {
    const objectUrl = URL.createObjectURL(file);

    return (
        <div>
            <h3>ACA DEBERIA ESTAR EL PPT</h3>
        </div>
    );
};

export default PptxViewer;
