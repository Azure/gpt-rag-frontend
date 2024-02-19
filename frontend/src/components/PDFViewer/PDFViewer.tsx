
import React, { useState, useEffect } from "react";
import { Worker, Viewer, SpecialZoomLevel } from "@react-pdf-viewer/core";

import "@react-pdf-viewer/core/lib/styles/index.css";
import "@react-pdf-viewer/default-layout/lib/styles/index.css";

interface LazyPdfViewerProps {
    base64Pdf: string | undefined;
    page: number | undefined;
}

const PdfViewer: React.FC<LazyPdfViewerProps> = ({ base64Pdf, page }) => {
    const [currentPage, setCurrentPage] = useState<number | undefined>(page);

    useEffect(() => {
        setCurrentPage(page);
    }, [base64Pdf]);

    const base64toBlob = (data: string | undefined) => {
        if (data === undefined) {
            return new Blob();
        }
        const base64WithoutPrefix = data.substr("data:application/pdf;base64,".length);

        const bytes = atob(base64WithoutPrefix);
        let length = bytes.length;
        let out = new Uint8Array(length);

        while (length--) {
            out[length] = bytes.charCodeAt(length);
        }

        return new Blob([out], { type: "application/pdf" });
    };

    const blob = base64toBlob(base64Pdf);
    const url = URL.createObjectURL(blob);

    return (
        <div>
            {base64Pdf ? (
                <>
                    <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.4.120/build/pdf.worker.min.js">
                        <div style={{ height: "750px" }}>
                            <Viewer fileUrl={url} defaultScale={SpecialZoomLevel.ActualSize} initialPage={currentPage ? currentPage - 1 : 0} />
                        </div>
                    </Worker>
                </>
            ) : (
                <div>Cargando PDF...</div>
            )}
        </div>
    );
};

export default PdfViewer;

