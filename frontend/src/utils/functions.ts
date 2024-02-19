export function getPagePDF(citations: string): number | undefined {
    const match = citations.match(/\.pdf:\s*(\d+)/);

    if (match) {
        const numero = parseFloat(match[1].trim());

        return isNaN(numero) ? undefined : numero;
    }

    return undefined;
}
