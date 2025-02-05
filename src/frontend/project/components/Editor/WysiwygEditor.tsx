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
  getDefaultReactSlashMenuItems,
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
  const { isDarkMode, currentPost } = useEditorStore();
  const editor = useCreateBlockNote();

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

  // Custom Slash Menu Items:
  // We include the default slash menu items and add two custom ones.
  // When selected, they will open the URL or Media suggestion menus.
  const getCustomSlashMenuItems = (editor: any): DefaultReactSuggestionItem[] => {
    const defaultItems = getDefaultReactSlashMenuItems(editor);
    const customURLItem = {
      title: "Insert URL",
      onItemClick: () => {
        // Close the slash menu (if needed) and open the URL suggestion menu.
        editor.openSuggestionMenu("@");
      },
      aliases: ["url", "link"],
      group: "Media/Links",
      subtext: "Select a URL from your references",
    };
    const customMediaItem = {
      title: "Insert Media",
      onItemClick: () => {
        // Close the slash menu and open the Media suggestion menu.
        editor.openSuggestionMenu("$");
      },
      aliases: ["media", "image", "video"],
      group: "Media/Links",
      subtext: "Select media from your references",
    };
    return [...defaultItems, customURLItem, customMediaItem];
  };

  // URL suggestion items for when "@" is triggered.
  const getUrlSuggestionMenuItems = (editor: any): DefaultReactSuggestionItem[] => {
    const urlReferences =
      ((currentPost?.urls ?? []).length > 0
        ? currentPost?.urls?.map((urlObj: any) => urlObj.url)
        : ["https://www.example.com", "https://www.anotherexample.com"]) ?? [];

    return urlReferences.map((url: string) => ({
      title: url,
      onItemClick: () => {
        const cursorPosition = editor.getTextCursorPosition();
        const currentBlock = cursorPosition ? cursorPosition.block : null;
        const linkBlock: PartialBlock = {
          type: "paragraph",
          content: [
            {
              type: "link",
              href: url,
              content: [{ type: "text", text: url, styles: {} }],
            }
          ],
        };
        if (currentBlock) {
          editor.insertBlocks([linkBlock], currentBlock, "after");
        } else {
          editor.appendBlocks([linkBlock]);
        }
      },
    }));
  };

  // Media suggestion items for when "$" is triggered.
  const getMediaSuggestionMenuItems = (editor: any): DefaultReactSuggestionItem[] => {
    const mediaReferences =
      ((currentPost?.media ?? []).length > 0
        ? currentPost?.media.map((media: any) => ({
            url: media.url,
            type: media.type || "image",
          }))
        : [{ url: "https://example.com/default-image.jpg", type: "image" }]) ?? [];

    return mediaReferences.map((media: any) => ({
      title: media.url,
      onItemClick: () => {
        const cursorPosition = editor.getTextCursorPosition();
        const currentBlock = cursorPosition ? cursorPosition.block : null;
        const mediaBlock: PartialBlock = {
          type: media.type === "video" ? "video" : "image",
          props: {
            url: media.url,
            caption: "",
            ...(media.type === "video" ? { aspectRatio: "16/9" } : {}),
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
        // Disable the default slash menu so we can use our custom one.
        slashMenu={false}
        sideMenu={true}
        style={{
          flex: 1,
          overflowY: "auto",
          maxWidth: "900px",
          margin: "0 auto",
          width: "100%",
        }}
      >
        {/* Custom Slash Menu Controller with "/" trigger */}
        <SuggestionMenuController
          triggerCharacter={"/"}
          getItems={async (query: any) =>
            filterSuggestionItems(getCustomSlashMenuItems(editor), query)
          }
          minQueryLength={0}
        />

        {/* URL Suggestion Menu triggered by "@" */}
        <SuggestionMenuController
          triggerCharacter={"@"}
          getItems={async (query: any) =>
            filterSuggestionItems(getUrlSuggestionMenuItems(editor), query)
          }
          minQueryLength={0}
        />

        {/* Media Suggestion Menu triggered by "$" */}
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
