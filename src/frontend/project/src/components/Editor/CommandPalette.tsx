import React, { useState, useEffect, useRef, forwardRef } from 'react';
import {
  Image, Link, Video, Quote, ListOrdered, List, Hash, Twitter, Code, Table, Check, Heading1, Heading2, Heading3, FileText,
} from 'lucide-react';
import { SlashCommand } from '../../types';

interface CommandPaletteProps {
  isOpen: boolean;
  onSelect: (command: SlashCommand) => void;
  onClose: () => void;
  position: { x: number; y: number };
  currentPost?: any;
}

export const getCommands = (currentPost: any): SlashCommand[] => [
    {
        id: 'h1',
        title: 'Heading 1',
        description: 'Large heading',
        icon: <Heading1 className="w-4 h-4" />,
        action: () => '# ',
    },
    {
        id: 'h2',
        title: 'Heading 2',
        description: 'Medium heading',
        icon: <Heading2 className="w-4 h-4" />,
        action: () => '## ',
    },
    {
        id: 'h3',
        title: 'Heading 3',
        description: 'Small heading',
        icon: <Heading3 className="w-4 h-4" />,
        action: () => '### ',
    },
    {
        id: 'twitter',
        title: 'Twitter Embed',
        description: 'Embed a tweet',
        icon: <Twitter className="w-4 h-4" />,
        action: () => currentPost?.tweet?.id
            ? `{{< twitter id="${currentPost.tweet.id}" >}}\n`
            : '{{< twitter id="PASTE_TWEET_ID_HERE" >}}\n',
    },
    {
        id: 'image',
        title: 'Image',
        description: 'Insert an image',
        icon: <Image className="w-4 h-4" />,
        action: () => currentPost?.media?.[0]?.original_url && currentPost?.media?.[0].type === 'photo'
            ? `![](${currentPost.media[0].original_url})\n`
            : '![]()\n',
    },
    {
        id: 'link',
        title: 'Link',
        description: 'Insert a link',
        icon: <Link className="w-4 h-4" />,
        action: () => currentPost?.urls?.[0]?.original_url
            ? `[${currentPost.urls[0].original_url}](${currentPost.urls[0].original_url})`
            : '[]()',
    },
    {
        id: 'quote',
        title: 'Blockquote',
        description: 'Insert a quote',
        icon: <Quote className="w-4 h-4" />,
        action: () => '> ',
    },
    {
        id: 'code',
        title: 'Code Block',
        description: 'Insert a code block',
        icon: <Code className="w-4 h-4" />,
        action: () => '```\n\n```',
    },
    {
        id: 'inlineCode',
        title: 'Inline Code',
        description: 'Insert inline code',
        icon: <Code className="w-4 h-4" />,
        action: () => '`',
    },
    {
        id: 'table',
        title: 'Table',
        description: 'Insert a table',
        icon: <Table className="w-4 h-4" />,
        action: () =>
            '| Header 1 | Header 2 |\n|----------|----------|\n| Cell 1   | Cell 2   |\n',
    },
    {
        id: 'checklist',
        title: 'Checklist',
        description: 'Insert a checklist',
        icon: <Check className="w-4 h-4" />,
        action: () => '- [ ] ',
    },
    {
        id: 'ol',
        title: 'Ordered List',
        description: 'Insert numbered list',
        icon: <ListOrdered className="w-4 h-4" />,
        action: () => '1. ',
    },
    {
        id: 'ul',
        title: 'Unordered List',
        description: 'Insert bullet list',
        icon: <List className="w-4 h-4" />,
        action: () => '- ',
    },
    {
        id: 'hr',
        title: 'Horizontal Rule',
        description: 'Insert a divider',
        icon: <FileText className="w-4 h-4" />,
        action: () => '---\n',
    },
    {
        id: 'tags',
        title: 'Tags',
        description: 'Insert tags',
        icon: <Hash className="w-4 h-4" />,
        action: () =>
            currentPost?.tags?.length
                ? `tags: [${currentPost.tags.join(', ')}]`
                : 'tags: []',
    },
    {
        id: 'video',
        title: 'Video',
        description: 'Insert a video embed',
        icon: <Video className="w-4 h-4" />,
        action: () =>
            currentPost?.media?.[0].original_url && currentPost?.media?.[0].type === 'video'
                ? `<video src="${currentPost.media[0].original_url}" controls></video>\n`
                : '<video src="PASTE_VIDEO_URL_HERE" controls></video>\n',
    },
    {
        id: 'tagReference',
        title: 'Tag Reference',
        description: 'Insert tag reference',
        icon: <Hash className="w-4 h-4" />,
        action: () => '#tag',
    },
    {
        id: 'metadata',
        title: 'Metadata',
        description: 'Insert metadata',
        icon: <Hash className="w-4 h-4" />,
        action: () => {
            const date = new Date(currentPost.createdAt);
            const formattedDate = date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
            });
            return `---\nblogpost: true\ncategory: LLM\ndate: ${formattedDate} \nauthor: Anukool Chaturvedi\ntags: ${currentPost.tags.join(', ')} \nlanguage: English\nexcerpt: 1\n---`;
        },
    },
];

export const CommandPalette = forwardRef<HTMLDivElement, CommandPaletteProps>(
  ({ isOpen, onSelect, onClose, position, currentPost }, forwardedRef) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedIndex, setSelectedIndex] = useState(0);
    const inputRef = useRef<HTMLInputElement>(null);
    const localRef = useRef<HTMLDivElement>(null);

    const containerRef = forwardedRef || localRef;

    const commands = getCommands(currentPost);

    const filteredCommands = commands.filter((command) =>
      command.title.toLowerCase().includes(searchQuery.toLowerCase())
    );

    useEffect(() => {
      if (isOpen && inputRef.current) {
        inputRef.current.focus();
      }
      setSelectedIndex(0);
    }, [isOpen, searchQuery]);

    useEffect(() => {
        if (isOpen && containerRef && 'current' in containerRef && containerRef.current) {
          const container = containerRef.current;
          const rect = container.getBoundingClientRect();
          const viewportHeight = window.innerHeight;
          const viewportWidth = window.innerWidth;
  
          // Check if the palette would go below viewport
          if (position.y + rect.height > viewportHeight) {
            container.style.top = `${viewportHeight - rect.height - 10}px`;
          } else {
            container.style.top = `${position.y}px`;
          }
  
          // Check if the palette would go beyond right edge of viewport
          if (position.x + rect.width > viewportWidth) {
            container.style.left = `${viewportWidth - rect.width - 10}px`;
          } else {
            container.style.left = `${position.x}px`;
          }
        }
      }, [isOpen, position, containerRef]);
  
      const handleKeyDown = (e: React.KeyboardEvent) => {
        e.stopPropagation();
  
        switch (e.key) {
          case 'ArrowDown':
            e.preventDefault();
            setSelectedIndex((i) => (i + 1) % filteredCommands.length);
            break;
          case 'ArrowUp':
            e.preventDefault();
            setSelectedIndex((i) => (i - 1 + filteredCommands.length) % filteredCommands.length);
            break;
          case 'Enter':
            e.preventDefault();
            if (filteredCommands[selectedIndex]) {
              onSelect(filteredCommands[selectedIndex]);
            }
            break;
          case 'Escape':
            e.preventDefault();
            onClose();
            break;
        }
      };

    const handleCommandClick = (command: SlashCommand) => {
      onSelect(command);
      onClose();
    };

    const handleMouseEnter = (index: number) => {
      setSelectedIndex(index);
    };

    if (!isOpen) return null;

    return (
        <div
          ref={containerRef}
          style={{
            position: 'fixed',
            zIndex: 1000,
          }}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-xl border dark:border-gray-700 overflow-hidden w-80 command-palette"
        >
          <div className="p-2 border-b dark:border-gray-700">
            <input
              ref={inputRef}
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full px-2 py-1 bg-transparent border-none outline-none dark:text-white"
              placeholder="Type to search..."
            />
          </div>
          <div className="max-h-64 overflow-y-auto">
            {filteredCommands.map((command, index) => (
              <button
                key={command.id}
                onClick={() => handleCommandClick(command)}
                onMouseEnter={() => handleMouseEnter(index)}
                className={`w-full text-left px-3 py-2 flex items-center gap-3 ${
                  index === selectedIndex
                    ? 'bg-blue-50 dark:bg-gray-700'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                {command.icon}
                <span>{command.title}</span>
              </button>
            ))}
          </div>
        </div>
      );
    }
  );

CommandPalette.displayName = 'CommandPalette';