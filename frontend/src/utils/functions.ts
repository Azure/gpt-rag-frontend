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
        case "jpeg":
        case "png":
        case "gif":
            return "image";
        default:
            return "unknown";
    }
}
