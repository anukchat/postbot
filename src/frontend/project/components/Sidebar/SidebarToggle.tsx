import React from 'react';
import { Menu, X } from 'lucide-react';
import Tippy from '@tippyjs/react';

interface SidebarToggleProps {
  isCollapsed: boolean;
  onClick: () => void;
}

export const SidebarToggle: React.FC<SidebarToggleProps> = ({ isCollapsed, onClick }) => {
  if (!isCollapsed) return null; // Only show when sidebar is collapsed

  return (
    <button
      onClick={onClick}
      className="fixed top-4 left-4 z-[40] p-2 bg-white dark:bg-gray-800 
        hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg shadow-lg
        transition-all duration-300"
      aria-label="Open menu"
    >
    <Tippy content="Toggle sidebar" placement="right">
        <Menu className="w-6 h-6" />
    </Tippy>
    </button>
  );
};
