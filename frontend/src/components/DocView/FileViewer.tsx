// frontend/src/components/DocView/FileViewer.tsx
import PDFViewer from "./PDFViewer";
import TextViewer from "./TextViewer";
import DocxViewer from "./DocxViewer";
import IMGViewer from "./IMGViewer";
import PptxViewer from "./PPTXViewer";
import XlsxViewer from "./XlsxViewer";

interface FileViewerProps {
    file: string | Blob;
    fileType: string;
    page?: number;
    fileName?: string;
}

const determineFileType = (fileType: string, fileName?: string) => {
    if (fileType && fileType !== "unknown") {
        return fileType;
    }

    const extension = fileName?.split('.').pop()?.toLowerCase();

    switch (extension) {
        case 'pdf':
            return 'pdf';
        case 'txt':
        case 'vtt':
            return 'txt';
        case 'docx':
            return 'docx';
        case 'pptx':
            return 'pptx';
        case 'xlsx':
            return 'xlsx';
        case 'jpg':
        case 'jpeg':
        case 'png':
            return 'jpg';
        default:
            return 'unknown';
    }
}

const FileViewer: React.FC<FileViewerProps> = ({ file, fileType, page, fileName }) => {
    const fileTypeToUse = determineFileType(fileType, fileName);

    let ViewerComponent: React.ComponentType<any> = () => <div>There is no viewer available for this type of file.</div>;
    let componentProps = { file, fileType: fileTypeToUse, page, fileName };

    switch (fileTypeToUse) {
        case "pdf":
            ViewerComponent = PDFViewer;
            componentProps.file = file;
            componentProps.page = page;
            break;
        case "txt":
        case "vtt":
        case "csv":
            ViewerComponent = TextViewer;
            break;
        case "docx":
            ViewerComponent = DocxViewer;
            componentProps.file = file;
            break;
        case "pptx":
            ViewerComponent = PptxViewer;
            componentProps.file = file;
            break;
        case "xlsx":
            ViewerComponent = XlsxViewer;
            componentProps.file = file;
            componentProps.fileName = fileName;
            break;
        case "jpg":
        case "png":
        case "jpeg":
            ViewerComponent = IMGViewer;
            componentProps.file = file;
            break;
        default:
            return <div>There is no viewer available for this type of file.</div>;
    }

    return <ViewerComponent {...componentProps} />;
};

export default FileViewer;
