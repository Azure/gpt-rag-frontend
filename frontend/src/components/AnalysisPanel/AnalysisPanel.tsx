import React, { Suspense, lazy } from "react";
import { Pivot, PivotItem } from "@fluentui/react";
import DOMPurify from "dompurify";
import { marked } from "marked";
import styles from "./AnalysisPanel.module.css";
import { AskResponse, Thought } from "../../api";
import { AnalysisPanelTabs } from "./AnalysisPanelTabs";

const LazyViewer = lazy(() => import("../DocView/DocView"));

interface Props {
    className: string;
    activeTab: AnalysisPanelTabs | undefined; // Allow undefined
    onActiveTabChanged: (tab: AnalysisPanelTabs) => void;
    activeCitation: string | undefined;
    citationHeight: string;
    answer: AskResponse;
    fileType?: string;
    fileName?: string;
}

const pivotItemDisabledStyle = { disabled: true, style: { color: "grey" } };

export const AnalysisPanel = ({
    answer,
    activeTab,
    onActiveTabChanged,
    activeCitation,
    citationHeight,
    className,
    fileType = 'txt', // Provide a default value
    fileName,       
}: Props) => {
    // Handle undefined activeTab
    if (!activeTab) {
        return null; // or render a default view
    }

    // Extract thoughts from answer
    const { thoughts } = answer;

    // Determine if thoughts exist and process them based on type
    let thoughtsContent: string = "";
    const MAX_CONTENT_LENGTH = 500;
    
    if (typeof thoughts === 'string') {
        thoughtsContent = thoughts.length > MAX_CONTENT_LENGTH 
            ? thoughts.substring(0, MAX_CONTENT_LENGTH) + "..." 
            : thoughts;
    } else if (Array.isArray(thoughts)) {
        // Map through the thoughts array and format each thought with truncation
        thoughtsContent = thoughts.map((thought: Thought) => {
            // Extract content, handling if it's a string or array
            let content = Array.isArray(thought.content) ? thought.content.join(' ') : thought.content;
    
            // Truncate content if it exceeds the max length
            content = content.length > MAX_CONTENT_LENGTH 
                ? content.substring(0, MAX_CONTENT_LENGTH) + "..." 
                : content;
    
            return `${thought.speaker}: ${content}`;
        }).join('<BR>'); // Join all thoughts with newline characters
    } else {
        thoughtsContent = ""; // Default to empty string if thoughts is undefined or null
    }

    const isDisabledThoughtProcessTab = !answer.thoughts || thoughtsContent.trim() === "";
    const isDisabledCitationTab = !activeCitation;

    const processedThoughts = thoughtsContent
        .replace(/[\[\]]/g, "") // Remove [ and ] characters
        .replace(/(user:|assistant:)/g, (match) => {
            return `<strong>${match}</strong>`;
        });

    const sanitizedHTML = DOMPurify.sanitize(marked.parse(processedThoughts, { async: false }));

    return (
        <Pivot
            className={className}
            selectedKey={activeTab}
            onLinkClick={(pivotItem) => {
                if (pivotItem) {
                    onActiveTabChanged(pivotItem.props.itemKey as AnalysisPanelTabs);
                }
            }}
        >
            {/* Thought Process Tab */}
            <PivotItem
                itemKey={AnalysisPanelTabs.ThoughtProcessTab}
                headerText="Thought process"
                headerButtonProps={
                    isDisabledThoughtProcessTab ? pivotItemDisabledStyle : undefined
                }
            >
                <div className={styles.thoughtProcessTabPane}>
                <div
                    dangerouslySetInnerHTML={{
                        __html: sanitizedHTML,
                    }}
                />

                </div>
            </PivotItem>

            {/* Citation Tab */}
            {activeCitation && (
                <PivotItem
                    itemKey={AnalysisPanelTabs.CitationTab}
                    headerText="Citation"
                    headerButtonProps={
                        isDisabledCitationTab ? pivotItemDisabledStyle : undefined
                    }
                >
                    <div className={styles.citationTabPane}>
                        <Suspense fallback={<div>Loading document...</div>}>
                            <LazyViewer base64Doc={activeCitation} fileType={fileType} fileName={fileName} />
                        </Suspense>
                    </div>
                </PivotItem>
            )}
        </Pivot>
    );
};
