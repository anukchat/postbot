import React, { useEffect } from 'react';
import "@blocknote/core/fonts/inter.css";
import "@blocknote/mantine/style.css";
import "katex/dist/katex.min.css";
import { useCreateBlockNote } from "@blocknote/react";
import { BlockNoteView, lightDefaultTheme, darkDefaultTheme } from "@blocknote/mantine";
import katex from "katex";
import "../../styles/wysiwygStyles.css";
import { useEditorStore } from '../../store/editorStore';

interface WysiwygEditorProps {
  content: string;
  onChange?: (newContent: string) => void;
  readOnly?: boolean;
}
export const WysiwygEditor: React.FC<WysiwygEditorProps> = ({ 
  content, 
  onChange,
  readOnly = false 
}) => {
  const { isDarkMode } = useEditorStore();
  const editor = useCreateBlockNote();

  useEffect(() => {
    const loadContent = async () => {
      const currentMarkdown = await editor.blocksToMarkdownLossy(editor.document);
      if (currentMarkdown !== content) {
        if (content) {
          const processKaTeX = (text: string, isBlock: boolean = false) => {
            const delimiter = isBlock ? '$$' : '$';
            const parts = text.split(delimiter);
            return parts.map((part, index) => {
              if (index % 2 === 1) { // Math content
                try {
                  return katex.renderToString(part, {
                    throwOnError: false,
                    displayMode: isBlock
                  });
                } catch (error) {
                  console.error('KaTeX rendering error:', error);
                  return part;
                }
              }
              return part;
            }).join('');
          };

          // Process the content line by line
          const processedContent = content.split('\n').map(line => {
            // First process block equations
            let processed = processKaTeX(line, true);
            // Then process inline equations
            processed = processKaTeX(processed, false);
            return processed;
          }).join('\n');

          const blocks = await editor.tryParseMarkdownToBlocks(processedContent);
          editor.replaceBlocks(editor.document, blocks);
        } else {
          editor.replaceBlocks(editor.document, []);
        }
      }
    };
    loadContent();
  }, [content]);

  const handleChange = async () => {
    onChange && onChange(await editor.blocksToMarkdownLossy(editor.document));
  };

  return (
    <div
      className="custom-editor"
      style={{
        width: '100%',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      <BlockNoteView
        editor={editor}
        theme={isDarkMode ? darkDefaultTheme : lightDefaultTheme}
        editable={!readOnly}
        onChange={handleChange}
        formattingToolbar={true}
        emojiPicker={true}
        slashMenu={true}
        sideMenu={true}
        style={{
          flex: 1,
          overflowY: 'auto',
          maxWidth: '900px',
          margin: '0 auto',
          width: '100%'
        }}
      />
    </div>
  );
};