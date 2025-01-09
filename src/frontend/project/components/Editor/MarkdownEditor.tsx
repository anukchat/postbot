import React, { useCallback, useRef, useEffect, useState } from 'react';
import { useEditorStore } from '../../store/editorStore';
import { EditorStatusBar } from './EditorStatusBar';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkEmoji from 'remark-emoji';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { TwitterEmbed } from './TwitterEmbed';
import { ScrollPosition } from '../../types';
import rehypeRaw from 'rehype-raw';
import { Toolbar } from './Toolbar';
import { getCommands } from './CommandPalette';
import Picker from 'emoji-picker-react';
import emoji from 'emoji-dictionary'; // Add this import
import { Clipboard, Plus } from 'lucide-react'; // Add this import
import Tippy from '@tippyjs/react'; // Add this import
import 'tippy.js/dist/tippy.css'; // Add this import
import TurndownService from 'turndown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Twitter embed error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <div className="p-4 text-red-500">Failed to load tweet</div>;
    }

    return this.props.children;
  }
}

interface MarkdownEditorProps {
  content: string;
  onChange: (newContent: string) => void;
  selectedTab: 'blog' | 'twitter' | 'linkedin'; // Add selectedTab prop
}

export const MarkdownEditor: React.FC<MarkdownEditorProps> = ({ content, onChange, selectedTab }) => {
  const { currentPost, undo, redo } = useEditorStore();  // Get undo and redo from the store
  const textAreaRef = useRef<HTMLTextAreaElement>(null);
  const [selection, setSelection] = useState({ start: 0, end: 0 });
  const isUpdatingRef = useRef(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const textareaScrollRef = useRef<ScrollPosition>({ x: 0, y: 0 });
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  // const [commandPalettePosition, setCommandPalettePosition] = useState({ x: 0, y: 0 });
  const [filteredCommands, setFilteredCommands] = useState(getCommands(currentPost));
  const [selectedIndex, setSelectedIndex] = useState(0);
  const commandTriggeredRef = useRef(false);
  const [isEmojiPickerOpen, setIsEmojiPickerOpen] = useState(false);
  const [emojiPickerPosition, setEmojiPickerPosition] = useState({ x: 0, y: 0 });
  const previewRef = useRef<HTMLDivElement>(null); // Add this ref
  const [isCopied, setIsCopied] = useState(false); // Add this state
  const turndownService = new TurndownService();

  // useEffect(() => {
  //   fetchPosts({});
  // }, [fetchPosts]);

  useEffect(() => {
    if (isEmojiPickerOpen && textAreaRef.current) {
      textAreaRef.current.focus();
    }
  }, [isEmojiPickerOpen]);

  const handleCommandInsert = (commandText: string, replaceLength: number) => {
    if (!textAreaRef.current || !currentPost) return;

    const textarea = textAreaRef.current;
    const currentScroll = { x: textarea.scrollLeft, y: textarea.scrollTop };

    let newText;
    let newCursorPosition;

    if (commandText === '**' || commandText === '*' || commandText === '~~') {
      const selectedText = textarea.value.substring(selection.start, selection.end);
      newText = textarea.value.substring(0, selection.start) + commandText + selectedText + commandText + textarea.value.substring(selection.end);
      newCursorPosition = selection.start + commandText.length + selectedText.length;
    } else {
      newText = textarea.value.substring(0, selection.start - replaceLength) + commandText + textarea.value.substring(selection.end);
      newCursorPosition = selection.start - replaceLength + commandText.length;
    }

    onChange(newText);

    requestAnimationFrame(() => {
      if (textAreaRef.current) {
        textAreaRef.current.focus();
        textAreaRef.current.setSelectionRange(newCursorPosition, newCursorPosition);
        textAreaRef.current.scrollTo(currentScroll.x, currentScroll.y);
      }
    });

    setIsCommandPaletteOpen(false);
    commandTriggeredRef.current = false; // Reset the flag after command is inserted
  };

  const handleEmojiInsert = (emojiText: string, replaceLength: number) => {
    if (!textAreaRef.current) return;

    const textarea = textAreaRef.current;
    const currentScroll = { x: textarea.scrollLeft, y: textarea.scrollTop };

    const newText = selection.start < 0
      ? emojiText + textarea.value.substring(selection.end)
      : textarea.value.substring(0, selection.start - replaceLength - 1) + emojiText + textarea.value.substring(selection.end);
    onChange(newText);

    const newCursorPosition = selection.start - replaceLength - 1 + emojiText.length;

    requestAnimationFrame(() => {
      if (textAreaRef.current) {
        textAreaRef.current.focus();
        textAreaRef.current.setSelectionRange(newCursorPosition, newCursorPosition);
        textAreaRef.current.scrollTo(currentScroll.x, currentScroll.y);
      }
    });
  };

  const handleEmojiClick = (event: any) => {
    handleEmojiInsert(event.emoji, 0);
    setIsEmojiPickerOpen(false);
    if (textAreaRef.current) {
      textAreaRef.current.focus();
    }
  };

  const handleContentChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const textarea = e.target;
    isUpdatingRef.current = true;
    setSelection({ start: textarea.selectionStart, end: textarea.selectionEnd });
    if (textAreaRef.current) {
      textareaScrollRef.current = { x: textAreaRef.current.scrollLeft, y: textAreaRef.current.scrollTop };
    }
    onChange(textarea.value);
    isUpdatingRef.current = false;
  }, [onChange]);

  useEffect(() => {
    if (textAreaRef.current && isUpdatingRef.current) {
      textAreaRef.current.setSelectionRange(selection.start, selection.end);
      textAreaRef.current.focus();
      isUpdatingRef.current = false;
      if (textareaScrollRef.current) {
        textAreaRef.current.scrollTo(textareaScrollRef.current.x, textareaScrollRef.current.y);
      }
    }
  }, [content, selection]);

  const calculateCursorPosition = (textarea: HTMLTextAreaElement): { x: number; y: number } => {
    const mirror = document.createElement('div');
    const style = window.getComputedStyle(textarea);

    const styles = [
      'font-family',
      'font-size',
      'font-weight',
      'line-height',
      'letter-spacing',
      'padding-left',
      'padding-top',
      'width',
      'box-sizing'
    ];

    styles.forEach(key => {
      (mirror.style as unknown as CSSStyleDeclaration)[key as any] = style.getPropertyValue(key);
    });

    mirror.style.position = 'absolute';
    mirror.style.visibility = 'hidden';
    mirror.style.whiteSpace = 'pre-wrap';
    mirror.style.wordWrap = 'break-word';
    document.body.appendChild(mirror);

    const textBeforeCursor = textarea.value.substring(0, textarea.selectionStart);

    const textNode = document.createTextNode(textBeforeCursor);
    const spanNode = document.createElement('span');
    spanNode.textContent = 'M';
    mirror.appendChild(textNode);
    mirror.appendChild(spanNode);

    const coords = spanNode.getBoundingClientRect();
    const textareaCoords = textarea.getBoundingClientRect();

    document.body.removeChild(mirror);

    return {
      x: (coords.left - textareaCoords.left) - textarea.scrollLeft,
      y: (coords.top - textareaCoords.top + coords.height) - textarea.scrollTop
    };
  };

  const updateCommandPalettePosition = (textarea: HTMLTextAreaElement) => {
    const position = calculateCursorPosition(textarea);
    const textareaRect = textarea.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;

    let x = textareaRect.left + position.x;
    let y = textareaRect.top + position.y;

    // Adjust if the palette goes beyond the viewport
    if (y + 200 > viewportHeight) { // Assuming the palette height is 200px
      y = viewportHeight - 210; // Adjust to fit within the viewport
    }
    if (x + 320 > viewportWidth) { // Assuming the palette width is 320px
      x = viewportWidth - 330; // Adjust to fit within the viewport
    }

    // setCommandPalettePosition({ x, y });
  };

  const handleKeyUp = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    const textarea = e.currentTarget;
    const value = textarea.value;
    const cursorPosition = textarea.selectionStart;
    const textBeforeCursor = value.substring(0, cursorPosition);

    if (textBeforeCursor.endsWith('/')) {
      updateCommandPalettePosition(textarea);
      setIsCommandPaletteOpen(true);
      setFilteredCommands(getCommands(currentPost));
      setSelectedIndex(0);
    } else {
      const lastSlashIndex = textBeforeCursor.lastIndexOf('/');
      if (lastSlashIndex !== -1 && cursorPosition - lastSlashIndex <= 10) {
        const searchTerm = textBeforeCursor.substring(lastSlashIndex + 1).toLowerCase();
        const filtered = getCommands(currentPost).filter(cmd =>
          cmd.title.toLowerCase().includes(searchTerm) ||
          cmd.description.toLowerCase().includes(searchTerm)
        );
        setFilteredCommands(filtered);
        setIsCommandPaletteOpen(filtered.length > 0);
        setSelectedIndex(0);
      } else {
        setIsCommandPaletteOpen(false);
      }
    }

    const emojiMatch = textBeforeCursor.match(/:([a-zA-Z0-9_+-]+):$/);
    if (emojiMatch) {
      const emojiCode = emojiMatch[1];
      const emojiChar = emoji.getUnicode(emojiCode);
      if (emojiChar) {
        handleEmojiInsert(emojiChar, emojiMatch[0].length);
      }
    }

    if (textBeforeCursor.endsWith(':')) {
      const { x, y } = textarea.getBoundingClientRect();
      setEmojiPickerPosition({ x, y: y + 20 });
      setIsEmojiPickerOpen(true);
    } else {
      setIsEmojiPickerOpen(false);
    }
  };

  const handleCommandSelect = (command: any) => {
    handleCommandInsert(command.action(), command.id.length + 1);
    setIsCommandPaletteOpen(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    commandTriggeredRef.current = false; // Reset the flag on every key down
    if (isCommandPaletteOpen) {
      updateCommandPalettePosition(e.currentTarget);
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex((prev) => (prev + 1) % filteredCommands.length);
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex((prev) => (prev - 1 + filteredCommands.length) % filteredCommands.length);
          break;
        case 'Enter':
          e.preventDefault();
          if (filteredCommands.length > 0) {
            handleCommandSelect(filteredCommands[selectedIndex]);
          }
          break;
        case 'Escape':
          e.preventDefault();
          setIsCommandPaletteOpen(false);
          break;
      }
    }

    if (e.ctrlKey || e.metaKey) {
      switch (e.key) {
        case 'z':
          e.preventDefault();
          undo(selectedTab);  // Use the undo from store
          break;
        case 'y':
          e.preventDefault();
          redo(selectedTab);  // Use the redo from store
          break;
        case 'b':
          e.preventDefault();
          handleCommandInsert('**', 0);
          break;
        case 'i':
          e.preventDefault();
          handleCommandInsert('*', 0);
          break;
        case 's':
          e.preventDefault();
          handleCommandInsert('~~', 0);
          break;
      }
    }
  };

  const handleSlashCommand = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    const textarea = e.currentTarget;
    const value = textarea.value;
    const cursorPosition = textarea.selectionStart;
    const textBeforeCursor = value.substring(0, cursorPosition);
    const lastSlashIndex = textBeforeCursor.lastIndexOf('/');

    if (lastSlashIndex !== -1 && cursorPosition === textBeforeCursor.length && !commandTriggeredRef.current) {
      const precedingChar = lastSlashIndex > 0 ? textBeforeCursor[lastSlashIndex - 1] : ' ';
      if (precedingChar === ' ' || precedingChar === '\n' || lastSlashIndex === 0) {
        const commandText = textBeforeCursor.substring(lastSlashIndex + 1).toLowerCase();
        const command = getCommands(currentPost).find(cmd => cmd.id === commandText);
        if (command) {
          handleCommandInsert(command.action(), commandText.length + 1); // +1 for the leading '/'
          commandTriggeredRef.current = true; // Set the flag to prevent repeated triggering
          e.preventDefault();
        }
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
        return (
          <ErrorBoundary>
            <div className="relative">
              <TwitterEmbed tweetId={tweetMatch[1]} />
            </div>
          </ErrorBoundary>
        );
      }

      return <p>{children}</p>;
    },
    pre: ({ children }: { children?: React.ReactNode }) => {
      const content = children?.toString() || '';
      const metadataMatch = content.match(/^---\nblogpost: true\ncategory: .*\ndate: .*\nauthor: .*\ntags: .*\nlanguage: .*\nexcerpt: .*\n---$/);

      if (metadataMatch) {
        return null; // Do not render metadata as a preview
      }

      return <pre>{children}</pre>;
    },
  };

  const filterMetadata = (content: string) => {
    const metadataRegex = /^---\n(?:.*\n)*?---\n/;
    return content.replace(metadataRegex, '');
  };

  const handleCopy = () => {
    if (previewRef.current) {
      const htmlContent = previewRef.current.innerHTML;
      // Convert HTML to Markdown
      const markdownContent = turndownService.turndown(htmlContent);
      
      // Create a temporary element to hold both formats
      const clipboardData = new ClipboardItem({
        'text/plain': new Blob([markdownContent], { type: 'text/plain' }),
        'text/html': new Blob([htmlContent], { type: 'text/html' })
      });

      navigator.clipboard.write([clipboardData]).then(() => {
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 1500);
      }).catch(err => {
        console.error('Failed to copy: ', err);
      });
    }
  };

  return (
    <>
      {!currentPost ? (
        <div className="flex items-center justify-center w-full h-full min-h-screen gap-3">
          <Plus className="w-8 h-8 text-gray-400" />
          <p className="text-gray-500 text-lg">Generate new or select existing post to edit</p>
        </div>
      ) : (
        <div className="flex flex-col h-full" ref={containerRef}>
          <div className="border-b flex items-center justify-center p-2 bg-gray-50 dark:bg-gray-800 sticky top-0 z-10">
            <div className="flex items-center space-x-2 overflow-x-auto">
              <Toolbar onCommandInsert={handleCommandInsert} selectedTab={selectedTab} />
            </div>
          </div>
          <div className="flex-1 relative overflow-auto">
            <PanelGroup 
              direction={window.innerWidth < 768 ? "vertical" : "horizontal"}
              className="min-h-0"
            >
              <Panel 
                defaultSize={50} 
                minSize={30}
                className="min-w-[250px] min-h-[300px]"
              >
                <textarea
                  ref={textAreaRef}
                  className="w-full h-full p-4 resize-none focus:outline-none dark:bg-gray-900 dark:text-white min-h-[300px]"
                  value={content}
                  onChange={handleContentChange}
                  onKeyUp={handleKeyUp}
                  onKeyDown={(e) => {
                    handleKeyDown(e);
                    handleSlashCommand(e);
                  }}
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
                  readOnly={currentPost?.status === 'Published'}
                />
                {isEmojiPickerOpen && (
                  <div
                    className="absolute z-10"
                    style={{
                      top: emojiPickerPosition.y,
                      left: emojiPickerPosition.x,
                    }}
                    tabIndex={-1}
                  >
                    <Picker onEmojiClick={handleEmojiClick} />
                  </div>
                )}
              </Panel>

              {/* Fixed ResizeHandle styles */}
              <PanelResizeHandle 
                className="group/handle" 
                style={{ 
                  position: 'relative',
                  outline: 'none'
                }}
              >
                <div className={`
                  absolute top-0 left-0 
                  ${window.innerWidth < 768 
                    ? 'h-1 w-full cursor-row-resize -translate-y-1/2' 
                    : 'w-1 h-full cursor-col-resize -translate-x-1/2'
                  }
                  bg-gray-200 dark:bg-gray-700 
                  group-hover/handle:bg-blue-500 
                  transition-colors
                  rounded-full
                `} />
              </PanelResizeHandle>

              <Panel 
                defaultSize={50}
                minSize={30}
                className="min-w-[250px] min-h-[300px]"
              >
                <div className="h-full overflow-auto p-4 prose dark:prose-invert max-w-none relative">
                  <Tippy content="Copy to clipboard">
                    <button
                    onClick={handleCopy}
                    className={`absolute top-2 right-2 p-1 rounded ${isCopied ? 'bg-green-500' : 'bg-gray-200 dark:bg-gray-700'}`}
                    title="Copy to clipboard"
                    >
                    <Clipboard className="w-4 h-4" />
                    </button>
                  </Tippy>
                  <div ref={previewRef}>
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm, remarkEmoji, remarkMath]}
                      rehypePlugins={[rehypeRaw, rehypeKatex]}
                      components={customComponents}
                    >
                      {filterMetadata(content)}
                    </ReactMarkdown>
                  </div>
                </div>
              </Panel>
            </PanelGroup>
          </div>
          {currentPost && <EditorStatusBar post={currentPost} />}
        </div>
      )}
    </>
  );
};