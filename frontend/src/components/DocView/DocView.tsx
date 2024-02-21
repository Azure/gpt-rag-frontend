import React, { useState, useEffect } from "react";
import { Worker, Viewer, SpecialZoomLevel } from "@react-pdf-viewer/core";

import "@react-pdf-viewer/core/lib/styles/index.css";
import "@react-pdf-viewer/default-layout/lib/styles/index.css";

import DocViewer, { DocViewerRenderers } from "@cyntler/react-doc-viewer";

interface LazyDocViewerProps {
    base64Doc: string | undefined;
    page?: number | undefined;
    fileType: string;
}

const DocView: React.FC<LazyDocViewerProps> = ({ base64Doc, page, fileType }) => {
    const [currentPage, setCurrentPage] = useState<number | undefined>(page);

    useEffect(() => {
        setCurrentPage(page);
    }, [base64Doc]);

    const base64toBlob = (data: string | undefined) => {
        if (data === undefined) {
            return new Blob();
        }
        const base64WithoutPrefix = data.substr(data.indexOf(",") + 1);

        const bytes = atob(base64WithoutPrefix);
        let length = bytes.length;
        let out = new Uint8Array(length);

        while (length--) {
            out[length] = bytes.charCodeAt(length);
        }

        return new Blob([out]);
    };

    const blob = base64toBlob(base64Doc);
    const url = URL.createObjectURL(blob);
    const isPdf = fileType === "pdf";

    return (
        <div>
            {base64Doc ? (
                <>
                    {isPdf ? (
                        <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.4.120/build/pdf.worker.min.js">
                            <div style={{ height: "750px" }}>
                                <Viewer fileUrl={url} defaultScale={SpecialZoomLevel.ActualSize} initialPage={currentPage ? currentPage - 1 : 0} />
                            </div>
                        </Worker>
                    ) : (
                        <div style={{ height: "750px" }}>
                            <DocViewer documents={[{ uri: url }]} pluginRenderers={DocViewerRenderers} />
                        </div>
                    )}
                </>
            ) : (
                <div>Cargando Documento...</div>
            )}
        </div>
    );
};

export default DocView;
