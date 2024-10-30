import React, { Suspense, lazy } from "react";
import { Pivot, PivotItem } from "@fluentui/react";
import DOMPurify from "dompurify";
import { marked } from "marked";
import styles from "./AnalysisPanel.module.css";
import { AskResponse } from "../../api";
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

    const isDisabledThoughtProcessTab = !answer.thoughts || answer.thoughts.trim() === "";
    const isDisabledCitationTab = !activeCitation;

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
                        __html: DOMPurify.sanitize(
                            marked.parse(
                                (answer.thoughts || "")
                                .replace(/[\[\]]/g, "") // Remove [ and ] characters
                                .replace(/(Next speaker:|Agents group chat:)\s*\w+/g, (match) => {
                                    return `<strong>${match}</strong>`;
                                }),
                                { async: false }
                            )
                        ),
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
