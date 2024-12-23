import React, { useCallback, useState, useRef, useEffect } from 'react';
import { useEditorStore } from '../../store/editorStore';
import { EditorStatusBar } from './EditorStatusBar';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { TwitterEmbed } from './TwitterEmbed';
import { ScrollPosition, SlashCommand } from '../../types';
import rehypeRaw from 'rehype-raw';
import { Toolbar } from './Toolbar';
import { CommandPalette } from './CommandPaletteold';

const commands: SlashCommand[] = [
  { id: 'h1', title: 'Heading 1', description: 'Insert a level 1 heading', action: () => '# ' },
  { id: 'h2', title: 'Heading 2', description: 'Insert a level 2 heading', action: () => '## ' },
  { id: 'h3', title: 'Heading 3', description: 'Insert a level 3 heading', action: () => '### ' },
  { id: 'img', title: 'Insert image', description: 'Insert an image', action: () => '![]()' },
  { id: 'link', title: 'Insert link', description: 'Insert a link', action: () => '[]()' },
  { id: 'quote', title: 'Insert quote', description: 'Insert a blockquote', action: () => '> ' },
  { id: 'code', title: 'Insert code block', description: 'Insert a code block', action: () => '```\n\n```' },
  { id: 'inline', title: 'Insert inline code', description: 'Insert inline code', action: () => '`' },
  { id: 'table', title: 'Insert table', description: 'Insert a table', action: () => '| Header 1 | Header 2 |\n|----------|----------|\n| Cell 1   | Cell 2   |\n' },
  { id: 'checklist', title: 'Insert checklist', description: 'Insert a checklist', action: () => '- [ ] ' },
  { id: 'ol', title: 'Ordered list', description: 'Insert an ordered list', action: () => '1. ' },
  { id: 'ul', title: 'Unordered list', description: 'Insert an unordered list', action: () => '- ' },
  { id: 'hr', title: 'Horizontal rule', description: 'Insert a horizontal rule', action: () => '---\n' },
  { id: 'tags', title: 'Insert tags', description: 'Insert tags', action: () => 'tags: []' },
  { id: 'video', title: 'Insert video', description: 'Insert a video', action: () => '<video src="PASTE_VIDEO_URL_HERE" controls></video>\n' },
];

export const MarkdownEditor: React.FC = () => {
    const { currentPost, fetchPosts, updateContent, undo, redo } = useEditorStore();
    const textAreaRef = useRef<HTMLTextAreaElement>(null);
    const [selection, setSelection] = useState({ start: 0, end: 0 });
    const isUpdatingRef = useRef(false);
    const containerRef = useRef<HTMLDivElement>(null);
    const textareaScrollRef = useRef<ScrollPosition>({ x: 0, y: 0 });
    const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
    const [commandPalettePosition, setCommandPalettePosition] = useState({ x: 0, y: 0 });
    const [filteredCommands, setFilteredCommands] = useState<SlashCommand[]>(commands);

    useEffect(() => {
        fetchPosts({});
    }, [fetchPosts]);

    const handleCommandInsert = (commandText: string, replaceLength: number) => {
        if (!textAreaRef.current || !currentPost) return;

        const textarea = textAreaRef.current;
        const currentScroll = { x: textarea.scrollLeft, y: textarea.scrollTop };

        const newText = selection.start < 0
            ? commandText + textarea.value.substring(selection.end)
            : textarea.value.substring(0, selection.start - replaceLength) + commandText + textarea.value.substring(selection.end);
        updateContent(newText);

        const newCursorPosition = selection.start - replaceLength + commandText.length;

        requestAnimationFrame(() => {
            if (textAreaRef.current) {
                textAreaRef.current.focus();
                textAreaRef.current.setSelectionRange(newCursorPosition, newCursorPosition);
                textAreaRef.current.scrollTo(currentScroll.x, currentScroll.y);
            }
        });

        setIsCommandPaletteOpen(false);
    };

    const handleContentChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const textarea = e.target;
        isUpdatingRef.current = true;
        setSelection({ start: textarea.selectionStart, end: textarea.selectionEnd });
        if (textAreaRef.current) {
            textareaScrollRef.current = { x: textAreaRef.current.scrollLeft, y: textAreaRef.current.scrollTop };
        }
        updateContent(textarea.value);
    }, [updateContent]);

    useEffect(() => {
        if (textAreaRef.current && isUpdatingRef.current) {
            textAreaRef.current.setSelectionRange(selection.start, selection.end);
            textAreaRef.current.focus();
            isUpdatingRef.current = false;
            if (textareaScrollRef.current) {
                textAreaRef.current.scrollTo(textareaScrollRef.current.x, textareaScrollRef.current.y);
            }
        }
    }, [currentPost?.content, selection]);

    const handleKeyUp = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        const value = e.currentTarget.value;
        const cursorPosition = e.currentTarget.selectionStart;
        const textBeforeCursor = value.substring(0, cursorPosition);
        const textAfterCursor = value.substring(cursorPosition);

        if (textBeforeCursor.endsWith('/h1')) {
            handleCommandInsert('# ', 3);
        } else if (textBeforeCursor.endsWith('/h2')) {
            handleCommandInsert('## ', 3);
        } else if (textBeforeCursor.endsWith('/h3')) {
            handleCommandInsert('### ', 3);
        } else if (textBeforeCursor.endsWith('/img')) {
            handleCommandInsert('![]()', 4);
        } else if (textBeforeCursor.endsWith('/link')) {
            handleCommandInsert('[]()', 5);
        } else if (textBeforeCursor.endsWith('/quote')) {
            handleCommandInsert('> ', 6);
        } else if (textBeforeCursor.endsWith('/code')) {
            handleCommandInsert('```\n\n```', 5);
        } else if (textBeforeCursor.endsWith('/inline')) {
            handleCommandInsert('`', 7);
        } else if (textBeforeCursor.endsWith('/table')) {
            handleCommandInsert('| Header 1 | Header 2 |\n|----------|----------|\n| Cell 1   | Cell 2   |\n', 6);
        } else if (textBeforeCursor.endsWith('/checklist')) {
            handleCommandInsert('- [ ] ', 10);
        } else if (textBeforeCursor.endsWith('/ol')) {
            handleCommandInsert('1. ', 3);
        } else if (textBeforeCursor.endsWith('/ul')) {
            handleCommandInsert('- ', 3);
        } else if (textBeforeCursor.endsWith('/hr')) {
            handleCommandInsert('---\n', 3);
        } else if (textBeforeCursor.endsWith('/tags')) {
            handleCommandInsert('tags: []', 5);
        } else if (textBeforeCursor.endsWith('/video')) {
            handleCommandInsert('<video src="PASTE_VIDEO_URL_HERE" controls></video>\n', 6);
        } else if (textBeforeCursor.endsWith('/')) {
            const { x, y } = e.currentTarget.getBoundingClientRect();
            const cursorPosition = {
                x: x + e.currentTarget.selectionStart * 8, // Approximate character width
                y: y + 20, // Offset for the cursor height
            };
            setCommandPalettePosition(cursorPosition);
            setIsCommandPaletteOpen(true);
            setFilteredCommands(commands);
        } else {
            setIsCommandPaletteOpen(false);
        }
    };

    const handleCommandSelect = (command: SlashCommand) => {
        handleCommandInsert(command.action(), command.id.length + 1); // +1 for the leading '/'
        setIsCommandPaletteOpen(false);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'z':
                    e.preventDefault();
                    undo();
                    break;
                case 'y':
                    e.preventDefault();
                    redo();
                    break;
            }
        }
    };

    const customComponents = {
        code({ node, inline, className, children, ...props }: { node?: any; inline?: boolean; className?: string; children?: React.ReactNode }) {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
                <SyntaxHighlighter {...props} style={tomorrow} language={match[1]} PreTag="div">
                    {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
            ) : (
                <code {...props} className={className}>
                    {children}
                </code>
            );
        },
        p: ({ children }: { children?: React.ReactNode }) => {
            const content = children?.toString() || '';
            const tweetMatch = content.match(/{{< twitter id="([^"]+)" >}}/);

            if (tweetMatch) {
                return <TwitterEmbed tweetId={tweetMatch[1]} />;
            }
  
      return <p>{children}</p>;
    },
  };

  return (
    <div className="flex flex-col h-full" ref={containerRef}>
      <Toolbar onCommandInsert={handleCommandInsert} />
      <div className="flex-1 relative overflow-auto">
        <PanelGroup direction="horizontal">
          <Panel defaultSize={50}>
            <textarea
              ref={textAreaRef}
              className="w-full h-full p-4 resize-none focus:outline-none dark:bg-gray-900 dark:text-white"
              value={currentPost?.content || ''}
              onChange={handleContentChange}
              onKeyUp={handleKeyUp}
              onKeyDown={handleKeyDown}
              onSelect={(e) =>
                setSelection({
                  start: e.currentTarget.selectionStart,
                  end: e.currentTarget.selectionEnd,
                })
              }
              style={{
                overflowAnchor: 'none',
                overscrollBehavior: 'none',
              }}
            />
            {isCommandPaletteOpen && (
              <div
                className="absolute z-10 bg-white border border-gray-300 shadow-md rounded mt-1"
                style={{
                  top: commandPalettePosition.y + 20, // Adjust as needed
                  left: commandPalettePosition.x,
                  minWidth: '150px',
                }}
              >
                {filteredCommands.length > 0 ? (
                  filteredCommands.map((command) => (
                    <div
                      key={command.id}
                      className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                      onClick={() => handleCommandSelect(command)}
                    >
                      {command.title}
                    </div>
                  ))
                ) : (
                  <div className="px-4 py-2 text-gray-500">No matching commands</div>
                )}
              </div>
            )}
          </Panel>
          <PanelResizeHandle className="w-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 cursor-col-resize" />
          <Panel defaultSize={50}>
            <div className="h-full overflow-auto p-4 prose dark:prose-invert max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeRaw]}
                components={customComponents}
              >
                {currentPost?.content || ''}
              </ReactMarkdown>
            </div>
          </Panel>
        </PanelGroup>
      </div>
      {currentPost && <EditorStatusBar post={currentPost} />}
    </div>
  );
};