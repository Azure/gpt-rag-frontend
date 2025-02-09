import React, { Suspense, lazy } from "react";
import { Pivot, PivotItem } from "@fluentui/react";
import DOMPurify from "dompurify";
import styles from "./AnalysisPanel.module.css";
import { AskResponse, Thought } from "../../api";
import { AnalysisPanelTabs } from "./AnalysisPanelTabs";

const LazyViewer = lazy(() => import("../DocView/DocView"));

interface Props {
  className: string;
  activeTab: AnalysisPanelTabs | undefined;
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
  fileType = "txt",
  fileName,
}: Props) => {
  if (!activeTab) {
    return null; // or render a default view
  }

  // Extract thoughts from answer
  const { thoughts } = answer;
  let thoughtsContent: string = "";
  const MAX_CONTENT_LENGTH = 1000;

  if (typeof thoughts === "string") {
    thoughtsContent =
      thoughts.length > MAX_CONTENT_LENGTH
        ? thoughts.substring(0, MAX_CONTENT_LENGTH) + "..."
        : thoughts;
  } else if (Array.isArray(thoughts)) {
    // Build HTML blocks for each thought message with extra formatting
    thoughtsContent = thoughts
      .map((thought: Thought) => {
        // Handle content that can be a string or an array of strings
        let content = Array.isArray(thought.content)
          ? thought.content.join("<br>")
          : thought.content;

        // Truncate content if it's too long
        if (content.length > MAX_CONTENT_LENGTH) {
          content = content.substring(0, MAX_CONTENT_LENGTH) + "...";
        }

        return `
          <div class="message ${thought.speaker}">
            <div class="speaker"><strong>${thought.speaker}</strong></div>
            <div class="content">${content}</div>
          </div>
          <br/>
        `;
      })
      .join("");
  } else {
    thoughtsContent = "";
  }

  // Directly sanitize the HTML without any extra replacement
  const sanitizedHTML = DOMPurify.sanitize(thoughtsContent);

  // Define tab disabled states
  const isDisabledThoughtProcessTab = !answer.thoughts || thoughtsContent.trim() === "";
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
        headerButtonProps={isDisabledThoughtProcessTab ? pivotItemDisabledStyle : undefined}
      >
        <div className={styles.thoughtProcess}>
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
          headerButtonProps={isDisabledCitationTab ? pivotItemDisabledStyle : undefined}
        >
          <div className={styles.thoughtProcess}>
            <Suspense fallback={<div>Loading document...</div>}>
              <LazyViewer base64Doc={activeCitation} fileType={fileType} fileName={fileName} />
            </Suspense>
          </div>
        </PivotItem>
      )}
    </Pivot>
  );
};
