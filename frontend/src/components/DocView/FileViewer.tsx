import PDFViewer from "./PDFViewer";
import TextViewer from "./TextViewer";
import DocxViewer from "./DocxViewer";
import IMGViewer from "./IMGViewer";
import PptxViewer from "./PPTXViewer";

interface FileViewerProps {
    file: (string|Blob);
    fileType: string;
    page?: number;
}

const FileViewer: React.ComponentType<FileViewerProps> = ({ file, fileType, page }) => {
    console.log("Filetipe", fileType);
    let ViewerComponent: React.ComponentType<any> = () => <div>No hay visor disponible para este tipo de archivo.</div>;

    let componentProps = { file, fileType, page };

    switch (fileType) {
        case "pdf":
            ViewerComponent = PDFViewer;
            componentProps.file = file;
            componentProps.page = page;
            break;
        case "txt":
        case "cvs":
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
        case "jpg":
        case "png":
            ViewerComponent = IMGViewer;
            componentProps.file = file;
            break;
    }

    // @ts-ignore
    return <ViewerComponent {...componentProps} />;
};

export default FileViewer;
