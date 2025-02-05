import React, { useEffect } from "react";
import "@blocknote/core/fonts/inter.css";
import "@blocknote/mantine/style.css";
import "katex/dist/katex.min.css";
import { useCreateBlockNote } from "@blocknote/react";
import {
  BlockNoteView,
  lightDefaultTheme,
  darkDefaultTheme,
} from "@blocknote/mantine";
import {
  SuggestionMenuController,
  DefaultReactSuggestionItem,
} from "@blocknote/react";
import { filterSuggestionItems } from "@blocknote/core";
import { PartialBlock } from "@blocknote/core";
import katex from "katex";
import "../../styles/wysiwygStyles.css";
import { useEditorStore } from "../../store/editorStore";

interface WysiwygEditorProps {
  content: string;
  onChange?: (newContent: string) => void;
  readOnly?: boolean;
}

export const WysiwygEditor: React.FC<WysiwygEditorProps> = ({
  content,
  onChange,
  readOnly = false,
}) => {
  const { isDarkMode } = useEditorStore();
  const editor = useCreateBlockNote();
  const { currentPost } = useEditorStore();

  useEffect(() => {
    const loadContent = async () => {
      const currentMarkdown = await editor.blocksToMarkdownLossy(editor.document);
      if (currentMarkdown !== content) {
        if (content) {
          const processKaTeX = (text: string, isBlock: boolean = false) => {
            const delimiter = isBlock ? "$$" : "$";
            const parts = text.split(delimiter);
            return parts
              .map((part, index) => {
                if (index % 2 === 1) {
                  try {
                    return katex.renderToString(part, {
                      throwOnError: false,
                      displayMode: isBlock,
                    });
                  } catch (error) {
                    console.error("KaTeX rendering error:", error);
                    return part;
                  }
                }
                return part;
              })
              .join("");
          };

          const processedContent = content
            .split("\n")
            .map((line) => {
              let processed = processKaTeX(line, true);
              processed = processKaTeX(processed, false);
              return processed;
            })
            .join("\n");

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
    if (onChange) {
      onChange(await editor.blocksToMarkdownLossy(editor.document));
    }
  };

  // Define URL suggestion items that insert a new block containing a link.
  // In the default schema, a link inline node should have:
  //    type: "link"
  //    href: string
  //    content: an array of StyledText objects (with type "text", text, and styles)
  const getUrlSuggestionMenuItems = (editor: any): DefaultReactSuggestionItem[] => {
    const urlReferences = (currentPost?.urls || []).length > 0
      ? currentPost?.urls.map(urlObj => urlObj.url) ?? ["https://www.example.com"]
      : ["https://www.example.com", "https://www.anotherexample.com"];

    return urlReferences.map((url: any) => ({
      title: url,
      onItemClick: () => {
        // Safely get the current cursor position.
        const cursorPosition = editor.getTextCursorPosition();
        const currentBlock = cursorPosition ? cursorPosition.block : null;

        // Define a new block (paragraph) containing a link.
        // The link inline node follows the default schema:
        //  - "link" has a required href and a content array of styled text.
        const linkBlock: PartialBlock = {
          type: "paragraph",
          content: [
            {
              type: "link",
              href: url,
              content: [
                { type: "text", text: url, styles: {} },
              ],
            },
            { type: "text", text: " ", styles: {} },
          ],
        };

        // Insert the new block after the current block if available.
        if (currentBlock) {
          editor.insertBlocks([linkBlock], currentBlock, "after");
        } else {
          // Fallback: append the block if no current block is found.
          editor.appendBlocks([linkBlock]);
        }
      },
    }));
  };

  const getMediaSuggestionMenuItems = (editor: any): DefaultReactSuggestionItem[] => {
    const mediaReferences = ((currentPost?.media ?? []).length > 0)
      ? (currentPost?.media.map(media => ({
        url: media.url,
        type: media.type || 'image'
      })) ?? [])
      : [{ url: "https://example.com/default-image.jpg", type: "image" }];

    return mediaReferences.map((media: any) => ({
      title: media.url,
      onItemClick: () => {
      const cursorPosition = editor.getTextCursorPosition();
      const currentBlock = cursorPosition ? cursorPosition.block : null;

      const mediaBlock: PartialBlock = {
        type: media.type === 'photo' || 'image' ? 'image' : 'video',
        props: {
          url: media.url,
          caption: "",
          ...(media.type === 'video' ? { aspectRatio: "16/9" } : {})
        },
      };

      if (currentBlock) {
        editor.insertBlocks([mediaBlock], currentBlock, "after");
      } else {
        editor.appendBlocks([mediaBlock]);
      }
      },
    }));
    };

  return (
    <div
      className="custom-editor"
      style={{
        width: "100%",
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
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
          overflowY: "auto",
          maxWidth: "900px",
          margin: "0 auto",
          width: "100%",
        }}
      >
        {/* Additional Suggestion Menu for URL references.
            This menu opens when the user types the "[" character. */}
        <SuggestionMenuController
          triggerCharacter={"@"}
          getItems={async (query: any) =>
            filterSuggestionItems(getUrlSuggestionMenuItems(editor), query)
          }
          minQueryLength={0}
        />
        
        {/* Additional Suggestion Menu for Media references.
            This menu opens when the user types the "[" character. */}
        <SuggestionMenuController
          triggerCharacter={"$"}
          getItems={async (query: any) =>
            filterSuggestionItems(getMediaSuggestionMenuItems(editor), query)
          }
          minQueryLength={0}
        />
      </BlockNoteView>
    </div>
  );
};

export default WysiwygEditor;
