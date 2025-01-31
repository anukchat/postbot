import React, { useState, useEffect, useRef } from 'react';
import { Image, Link, Video, Quote, ListOrdered, List, Hash, Twitter } from 'lucide-react';
import { SlashCommand } from '../../types';

interface SlashCommandMenuProps {
    isOpen: boolean;
    onSelect: (command: SlashCommand) => void;
    onClose: () => void;
    position: { x: number; y: number };
  }

  
export const SlashCommandMenu: React.FC<SlashCommandMenuProps> = ({
  isOpen,
  onSelect,
  onClose,
  position
}) => {
  const menuRef = useRef<HTMLDivElement>(null);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const commands: SlashCommand[] = [
    {
      id: 'h1',
      title: 'Heading 1',
      action: () => '# ',
      description: ''
    },
    {
      id: 'h2',
      title: 'Heading 2',
      action: () => '## ',
      description: ''
    },
    {
      id: 'twitter',
      title: 'Twitter Embed',
      icon: <Twitter className="w-4 h-4" />,
      action: () => '{{< twitter id="PASTE_TWEET_ID_HERE" >}}\n',
      description: ''
    },
    {
      id: 'image',
      title: 'Image',
      icon: <Image className="w-4 h-4" />,
      action: () => '![]()\n',
      description: ''
    },
    {
      id: 'video',
      title: 'Video',
      icon: <Video className="w-4 h-4" />,
      action: () => '{{< video src="" >}}\n',
      description: ''
    },
    {
      id: 'link',
      title: 'Link',
      icon: <Link className="w-4 h-4" />,
      action: () => '[]()',
      description: ''
    },
    {
      id: 'quote',
      title: 'Quote',
      icon: <Quote className="w-4 h-4" />,
      action: () => '> ',
      description: ''
    },
    {
      id: 'ol',
      title: 'Ordered List',
      icon: <ListOrdered className="w-4 h-4" />,
      action: () => '1. ',
      description: ''
    },
    {
      id: 'ul',
      title: 'Unordered List',
      icon: <List className="w-4 h-4" />,
      action: () => '- ',
      description: ''
    },
    {
      id: 'tags',
      title: 'Tags',
      icon: <Hash className="w-4 h-4" />,
      action: () => 'tags: []',
      description: ''
    },
  ];

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      // Only close if click is not on menu or its children
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    const handleKeyDown = (event: KeyboardEvent) => {
      if (!isOpen) return;

      switch (event.key) {
        case 'Tab':
          event.preventDefault();
          setSelectedIndex((prev) => 
            event.shiftKey 
              ? (prev - 1 + commands.length) % commands.length 
              : (prev + 1) % commands.length
          );
          break;
        case 'Enter':
          event.preventDefault();
          onSelect(commands[selectedIndex]);
          break;
        case 'Escape':
          event.preventDefault();
          onClose();
          break;
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose, onSelect, commands, selectedIndex]);

  const handleCommandClick = (command: SlashCommand, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onSelect(command);
  };

  if (!isOpen) return null;

  return (
    <div
      ref={menuRef}
      style={{
        position: 'absolute',
        left: position.x,
        top: position.y + 20, // Add small offset to avoid overlapping cursor
        zIndex: 1000,
      }}
      className="w-64 bg-white dark:bg-gray-800 shadow-lg rounded-lg border dark:border-gray-700"
      onClick={(e) => e.stopPropagation()}
    >
      <div className="p-2">
        {commands.map((command, index) => (
          <button
            key={command.id}
            onClick={(e) => handleCommandClick(command, e)}
            className={`w-full text-left px-3 py-2 rounded flex items-center gap-2 ${
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
};
