import React from 'react';
import { MoreVertical, Eye, ArrowUpRight, AlertCircle } from 'lucide-react';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import Tippy from '@tippyjs/react';
import { Source } from '../../types';

interface SourceCardProps {
  source: Source;
  isSelected: boolean;
  onSelect: () => void;
  hasExistingBlog: boolean;
  existingBlogId?: string;
  onViewBlog: (blogId: string) => void;
  className?: string;
  children?: React.ReactNode;
}

export const SourceCard: React.FC<SourceCardProps> = ({
  source,
  isSelected,
  onSelect,
  hasExistingBlog,
  existingBlogId,
  onViewBlog,
  className,
  children
}) => {
  const handleViewBlogClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (existingBlogId) {
      onViewBlog(existingBlogId);
    }
  };

  return (
    <div 
      className={`relative group ${
        isSelected ? 'ring-2 ring-blue-500' : 'hover:ring-1 hover:ring-blue-300'
      } ${className}`}
      onClick={onSelect}
    >
      {/* Warning indicator - Update z-index and positioning */}
      {source?.source_type === 'twitter' && source.has_url === false && (
        <Tippy content="This tweet has no URLs. Content generation may be limited.">
          <div className="absolute top-2 right-2 z-[80]">
            <AlertCircle className="w-5 h-5 text-amber-500" />
          </div>
        </Tippy>
      )}

      {/* Blog availability indicator - Adjust left position to avoid overlap */}
      {hasExistingBlog && (
        <div className="absolute top-2 left-2 z-[70]">
          <div className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-full bg-green-100 text-green-800 dark:bg-green-900/80 dark:text-green-300 shadow-sm backdrop-blur-sm transition-opacity duration-200">
            <Eye className="w-3.5 h-3.5" />
            <span>Blog Available</span>
          </div>
        </div>
      )}

      {/* Context Menu - Move it slightly to avoid overlap with warning */}
      <div className="absolute top-2 right-10 z-[60] opacity-0 group-hover:opacity-100 transition-opacity">
        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <button 
              className="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
              onClick={(e) => e.stopPropagation()}
            >
              <MoreVertical className="w-4 h-4" />
            </button>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content 
              className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-[70]"
              sideOffset={5}
              align="end"
            >
              {hasExistingBlog && (
                <DropdownMenu.Item 
                  className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
                  onClick={handleViewBlogClick}
                >
                  <Eye className="w-4 h-4" />
                  View Blog
                </DropdownMenu.Item>
              )}
              <DropdownMenu.Item 
                className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
                onClick={(e) => {
                  e.stopPropagation();
                 
                const isTwitterUrl = source.source_identifier.includes('twitter.com');
                if (isTwitterUrl) {
                    window.open(`https://twitter.com/intent/tweet?url=${encodeURIComponent(source.source_identifier)}`, '_blank');
                }
                else {
                    window.open(source.source_identifier, '_blank');
                }
                }}
              >
                <ArrowUpRight className="w-4 h-4" />
                Open Original
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>
      </div>

      {children}
    </div>
  );
};
