import React, { useEffect } from 'react';
import "@blocknote/core/fonts/inter.css";
import "@blocknote/mantine/style.css";
import { BlockNoteEditor } from "@blocknote/core";
import { useCreateBlockNote } from "@blocknote/react";
import { BlockNoteView, lightDefaultTheme } from "@blocknote/mantine";

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
  const editor = useCreateBlockNote();

  useEffect(() => {
    const loadContent = async () => {
      const currentMarkdown = await editor.blocksToMarkdownLossy(editor.document);
      if (currentMarkdown !== content) {
        if (content) {
          const blocks = await editor.tryParseMarkdownToBlocks(content);
          editor.replaceBlocks(editor.document, blocks);
        } else {
          editor.replaceBlocks(editor.document, []);
        }
      }
    };
    loadContent();
  }, [content]); // Added content as a dependency

  const handleChange = async () => {
    onChange && onChange(await editor.blocksToMarkdownLossy(editor.document));
  };

  return (
    <div style={{ 
      width: '100%',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      <BlockNoteView
        editor={editor}
        theme={lightDefaultTheme}
        editable={!readOnly}
        onChange={handleChange}
        formattingToolbar={true}
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '20px',
          fontSize: '16px',
          maxWidth: '800px',
          margin: '0 auto',
          width: '100%'
        }}
      />
    </div>
  );
};