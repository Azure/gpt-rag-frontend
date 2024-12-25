import styles from "./UserChatMessage.module.css";

import { useEffect, useState } from "react";

interface Props {
    message: string;
    file: string | null; // Blob name
}

export const UserChatMessage = ({ message, file }: Props) => {
    const [blobUrl, setBlobUrl] = useState<string | null>(null);

    useEffect(() => {
        const fetchBlobFile = async () => {
            if (file) {
                try {
                    const response = await fetch("/api/get-blob", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({ blob_name: file }),
                    });

                    if (!response.ok) {
                        throw new Error(`Error fetching blob: ${response.statusText}`);
                    }

                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob); // Create a temporary URL for the blob
                    setBlobUrl(url);
                } catch (error) {
                    console.error("Failed to fetch blob file:", error);
                }
            }
        };

        fetchBlobFile();

        return () => {
            if (blobUrl) {
                URL.revokeObjectURL(blobUrl);
            }
        };
    }, [file]);

    return (
        <div className={styles.container}>
            <div className={styles.message}>{message}
            {file && blobUrl && (
                <div className={styles.file}>
                    {file.endsWith(".png") || file.endsWith(".jpg") || file.endsWith(".jpeg") ? (
                        <img
                            src={blobUrl}
                            alt="Blob Content"
                            className={styles.image} // Add this class for styling
                        />
                    ) : (
                        <a href={blobUrl} download={file} rel="noopener noreferrer">
                            {file.split("/").pop() || "Download File"}
                        </a>
                    )}
                </div>
            )}
        </div>
        </div>
    );
    
};