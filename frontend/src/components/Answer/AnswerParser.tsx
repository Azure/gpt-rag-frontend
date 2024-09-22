// src/components/Answer/AnswerParser.tsx

// Import necessary modules and types
import { getCitationFilePath } from "../../api";
import DOMPurify from "dompurify";
import { marked } from "marked";

// Define the structure of the parsed answer
type HtmlParsedAnswer = {
  answerHtml: string;
  citations: string[];
  followupQuestions: string[];
};

/**
 * Removes citations from the text.
 * Citations are assumed to be in the format [citation].
 *
 * @param text - The text from which to remove citations.
 * @returns The text without citations.
 */
export function removeCitations(text: string): string {
  return text.replace(/\[[^\]]*\]/g, "");
}

/**
 * Parses the answer string into sanitized HTML, extracts citations,
 * and identifies any follow-up questions.
 *
 * @param answer - The raw answer string containing Markdown and citations.
 * @param showSources - Flag to determine if citations should be displayed.
 * @param onCitationClicked - Callback for handling citation clicks.
 * @returns An object containing the sanitized HTML, list of citations, and follow-up questions.
 */
export function parseAnswerToHtml(
  answer: string,
  showSources: boolean,
  onCitationClicked: (citationFilePath: string, filename: string) => void
): HtmlParsedAnswer {
  const citations: string[] = [];
  const followupQuestions: string[] = [];

  // 1. Extract any follow-up questions enclosed in << >> and remove them from the answer.
  let parsedAnswer = answer.replace(/<<([^>>]+)>>/g, (_, content) => {
    followupQuestions.push(content.trim());
    return "";
  });

  // 2. Trim any whitespace from the end of the answer after removing follow-up questions.
  parsedAnswer = parsedAnswer.trim();

  let processedAnswer = parsedAnswer;

  if (showSources) {
    // 3. Replace citations with unique placeholders and collect them.
    // Citations are assumed to be in the format [citation].
    processedAnswer = processedAnswer.replace(/\[([^\]]+)\]/g, (_, citation) => {
      const trimmedCitation = citation.trim();
      if (!citations.includes(trimmedCitation)) {
        citations.push(trimmedCitation);
      }
      const citationIndex = citations.indexOf(trimmedCitation) + 1;
      // Use a unique placeholder to identify citations later.
      return `CITATION_MARKER_${citationIndex}`;
    });
  } else {
    // 4. If sources are not to be shown, remove citations entirely.
    processedAnswer = removeCitations(processedAnswer);
  }

  let htmlContent: string;

  if (showSources) {
    // 5. Use marked.parse to parse the Markdown with citation placeholders to HTML.
    htmlContent = marked.parse(processedAnswer) as string; // Type Assertion Added
    htmlContent = htmlContent.replace(/<\/?p>/g, '');
    
    // 6. Replace citation placeholders with actual HTML links.
    // These links include data attributes to store citation information.
    htmlContent = htmlContent.replace(/CITATION_MARKER_(\d+)/g, (_: string, index: string) => {
      const citationIndex = parseInt(index, 10);
      const citation = citations[citationIndex - 1];
      const path = getCitationFilePath(citation);

      // Return an anchor tag with data attributes and a unique class for event handling.
      return `<a class="supContainer citation-link" title="${DOMPurify.sanitize(
        citation
      )}" data-citation="${DOMPurify.sanitize(citation)}" data-path="${DOMPurify.sanitize(
        path
      )}" href="#"><sup>${citationIndex}</sup></a>`;
    });
  } else {
    // 7. If not showing sources, simply parse the Markdown to HTML.
    htmlContent = marked.parse(processedAnswer) as string; // Type Assertion Added
    htmlContent = htmlContent.replace(/<\/?p>/g, '');
  }

  // 8. Sanitize the HTML to prevent XSS attacks and allow specific tags and attributes.
  const sanitizedHtml = DOMPurify.sanitize(htmlContent, {
    ADD_TAGS: ["sup", "a"],
    ADD_ATTR: ["class", "title", "data-citation", "data-path", "href"],
  });

  return {
    answerHtml: sanitizedHtml,
    citations,
    followupQuestions,
  };
}
