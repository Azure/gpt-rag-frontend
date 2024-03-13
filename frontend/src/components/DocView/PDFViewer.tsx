import { Worker, Viewer as PDFrender, SpecialZoomLevel } from "@react-pdf-viewer/core";

import "@react-pdf-viewer/default-layout/lib/styles/index.css";
import "@react-pdf-viewer/core/lib/styles/index.css";

interface PDFRenderProps {
    file: Blob | MediaSource;
    page?: number;
    fileType?: string;
}

const PDFViewer: React.ComponentType<PDFRenderProps> = ({ file, page }) => {
    return (
        <div style={{ height: "750px" }}>
            <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js">
                <PDFrender fileUrl={URL.createObjectURL(file)} defaultScale={SpecialZoomLevel.ActualSize} initialPage={page ? page - 1 : 0} />
            </Worker>
        </div>
    );
};

export default PDFViewer;
