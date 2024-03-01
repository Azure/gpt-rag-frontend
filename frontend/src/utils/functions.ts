export function getPage(citations: string): number | undefined {
    const match = citations.match(/\.pdf:\s*(\d+)/);

    if (match) {
        const numero = parseFloat(match[1].trim());

        return isNaN(numero) ? undefined : numero;
    }

    return undefined;
}

export function getFileType(citation: string): string {
    const extension = citation.split(".").pop()?.toLowerCase();

    switch (extension) {
        case "pdf":
            return "pdf";
        case "doc":
        case "docx":
            return "docx";
        case "ppt":
        case "pptx":
            return "pptx";
        case "xls":
        case "xlsx":
            return "xlsx";
        case "jpg":
            return "jpg";
        case "jpeg":
            return "jpeg";
        case "png":
            return "png";
        case "gif":
            return "gif";
        case "txt":
            return "txt";
        default:
            return "unknown";
    }
}
