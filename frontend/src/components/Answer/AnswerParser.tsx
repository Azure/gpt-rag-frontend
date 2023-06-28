import { renderToStaticMarkup } from "react-dom/server";
import { getCitationFilePath } from "../../api";

type HtmlParsedAnswer = {
    answerHtml: string;
    citations: string[];
    followupQuestions: string[];
};

export function removeCitations(text: string): string {
    const newText = text.replace(/\[[^\]]*\]/g, '');
    return newText;
  }

export function parseAnswerToHtml(answer: string, showSources: boolean, onCitationClicked: (citationFilePath: string) => void): HtmlParsedAnswer {
    const citations: string[] = [];
    const followupQuestions: string[] = [];
    var answerHtml: string = "";  

    // Extract any follow-up questions that might be in the answer
    let parsedAnswer = answer.replace(/<<([^>>]+)>>/g, (match, content) => {
        followupQuestions.push(content);
        return "";
    });

    // trim any whitespace from the end of the answer after removing follow-up questions
    parsedAnswer.trim();
    if (showSources) {
        parsedAnswer;
        const parts = parsedAnswer.split(/\[([^\]]+)\]/g);

        const fragments: string[] = parts.map((part, index) => {
            if (index % 2 === 0) {
                return part;
            } else {
                let citationIndex: number;
                if (citations.indexOf(part) !== -1) {
                    citationIndex = citations.indexOf(part) + 1;
                } else {
                    citations.push(part);
                    citationIndex = citations.length;
                }
    
                const path = getCitationFilePath(part);
    
                return renderToStaticMarkup(
                    <a className="supContainer" title={part} onClick={() => onCitationClicked(path)}>
                        <sup>{citationIndex}</sup>
                    </a>
                );
            }
        });
        answerHtml = fragments.join("");
    
    } else {  
        answerHtml = removeCitations(parsedAnswer);
    } 

    return {
        answerHtml: answerHtml,
        citations,
        followupQuestions
    };
}
