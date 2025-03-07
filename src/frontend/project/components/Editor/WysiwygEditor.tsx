import React, { useEffect } from "react";
  import "@blocknote/core/fonts/inter.css";
  import "@blocknote/mantine/style.css";
  import {
    useCreateBlockNote,
    SuggestionMenuProps,
    SuggestionMenuController,
    DefaultReactSuggestionItem,
    getDefaultReactSlashMenuItems,
  } from "@blocknote/react";
  import { BlockNoteView, lightDefaultTheme, darkDefaultTheme } from "@blocknote/mantine";
  import { filterSuggestionItems } from "@blocknote/core";
  import { PartialBlock } from "@blocknote/core";
  import "../../styles/wysiwygStyles.css";
  import { useEditorStore } from "../../store/editorStore";

  // Extend the DefaultReactSuggestionItem type to include the preview property.
  interface CustomReactSuggestionItem extends DefaultReactSuggestionItem {
    preview?: string;
  }

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

    // Load content from markdown if it changes.
    useEffect(() => {
      const loadContent = async () => {
        const currentMarkdown = await editor.blocksToMarkdownLossy(editor.document);
        if (currentMarkdown !== content) {
          if (content) {
            const trimmedContent = content.trim();
            const blocks = await editor.tryParseMarkdownToBlocks(trimmedContent);
            // Instead of trying to modify block content which can have various types,
            // let's use the blocks directly as they come from the parser
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

    // Custom Slash Menu Items: add URL and Media items.
    const getCustomSlashMenuItems = (editor: any): DefaultReactSuggestionItem[] => {
      const defaultItems = getDefaultReactSlashMenuItems(editor);
      const customURLItem = {
        title: "Insert URL",
        onItemClick: () => {
          editor.openSuggestionMenu("@");
        },
        aliases: ["url", "link"],
        group: "Media/Links",
        subtext: "Select a URL from your references",
      };
      const customMediaItem = {
        title: "Insert Media",
        onItemClick: () => {
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
              },
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
    // Use our extended type so we can include a preview property.
    const getMediaSuggestionMenuItems = (editor: any): CustomReactSuggestionItem[] => {
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
        preview: media.url,
      }));
    };

    // Custom Media Suggestion Menu Component: show only image previews.
    // On hover, each image scales up for better visibility.
    const CustomMediaSuggestionMenu: React.FC<SuggestionMenuProps<CustomReactSuggestionItem>> = ({
      items,
      selectedIndex = 0,
      onItemClick,
    }) => {
      return (
        <div
          className="custom-suggestion-menu"
          style={{
            background: "#fff",
            border: "1px solid #ddd",
            borderRadius: 4,
            boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
            display: "flex",
            flexWrap: "wrap",
            padding: 4,
            position: "relative",
            zIndex: 1,
          }}
        >
          {items.map((item, index) => (
            <div
              key={item.title + index}
              className={`suggestion-item ${selectedIndex === index ? "selected" : ""}`}
              onClick={() => onItemClick?.(item)}
              style={{
                margin: 4,
                cursor: "pointer",
                position: "relative",
                width: 50,
                height: 50,
              }}
            >
              {item.preview && (
                <div
                  style={{
                    position: "relative",
                    width: "100%",
                    height: "100%",
                  }}
                >
                  <img
                    src={item.preview}
                    alt="preview"
                    style={{
                      width: "100%",
                      height: "100%",
                      objectFit: "cover",
                      borderRadius: 4,
                      transition: "transform 0.2s ease, z-index 0s",
                    }}
                    onMouseEnter={(e) => {
                      const parent = e.currentTarget.parentElement;
                      if (parent) {
                        parent.style.zIndex = "1000";
                      }
                      e.currentTarget.style.position = "absolute";
                      e.currentTarget.style.transform = "scale(3)";
                      e.currentTarget.style.transformOrigin = "center";
                      e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.2)";
                      e.currentTarget.style.border = "2px solid white";
                    }}
                    onMouseLeave={(e) => {
                      const parent = e.currentTarget.parentElement;
                      if (parent) {
                        parent.style.zIndex = "1";
                      }
                      e.currentTarget.style.position = "relative";
                      e.currentTarget.style.transform = "scale(1)";
                      e.currentTarget.style.boxShadow = "none";
                      e.currentTarget.style.border = "none";
                    }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      );
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
          slashMenu={false}
          sideMenu={true}
          className="editor-view"
          style={{
            flex: 1,
            overflowY: "auto",
            maxWidth: "900px",
            margin: "0 auto",
            width: "100%",
            paddingTop: "6rem",
            paddingBottom: "6rem",
            zIndex: "0"  // Add this line
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

          {/* Media Suggestion Menu triggered by "$" with custom component for image-only preview */}
          <SuggestionMenuController
            triggerCharacter={"$"}
            getItems={async (query: any) =>
              filterSuggestionItems(getMediaSuggestionMenuItems(editor), query)
            }
            suggestionMenuComponent={CustomMediaSuggestionMenu}
            minQueryLength={0}
          />
        </BlockNoteView>
      </div>
    );
  };

  export default WysiwygEditor;
