import React from 'react';
import { Menu, X } from 'lucide-react';
import Tippy from '@tippyjs/react';

interface SidebarToggleProps {
  isCollapsed: boolean;
  onClick: () => void;
}

export const SidebarToggle: React.FC<SidebarToggleProps> = ({ isCollapsed, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="fixed top-4 left-4 p-2 bg-white dark:bg-gray-800 
        hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg shadow-lg
        transition-all duration-300 z-30 cursor-pointer"
      aria-label={isCollapsed ? "Open menu" : "Close menu"}
    >
      <Tippy content={isCollapsed ? "Open sidebar" : "Close sidebar"} placement="right">
        {isCollapsed ? <Menu className="w-6 h-6" /> : <></>}
      </Tippy>
    </button>
  );
};
