import React, { useState } from 'react';
import { Home, Sun, Moon, Plus, Inbox } from 'lucide-react';
import Tippy from '@tippyjs/react';
import { useEditorStore } from '../../store/editorStore';
import { NewBlogModal } from '../Modals/NewBlogModal';
import { Link } from 'react-router-dom';

interface FloatingNavProps {
  onToggleDrawer: () => void;
  isDrawerOpen: boolean;
}

export const FloatingNav: React.FC<FloatingNavProps> = ({ onToggleDrawer, isDrawerOpen }) => {
  const { toggleTheme, isDarkMode } = useEditorStore();
  const [isNewBlogModalOpen, setIsNewBlogModalOpen] = useState(false);

  return (
    <>
      <div className="fixed left-0 top-0 bottom-0 w-16 bg-white dark:bg-gray-800 border-r dark:border-gray-700 z-50">
        <div className="flex flex-col items-center gap-6 pt-6">
          {/* Logo */}
          <Link to="/" className="flex items-center mb-4">
            <img
              src="/assets/riteup logo svg.svg"
              alt="RiteUp Logo"
              className="h-10 w-auto transition-transform duration-300 hover:scale-105"
            />
          </Link>
          <Tippy content="Home" placement="right">
            <button 
              onClick={() => window.location.href = "/dashboard"}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all"
            >
              <Home className="w-5 h-5" />
            </button>
          </Tippy>
          
          <Tippy content={isDarkMode ? "Light mode" : "Dark mode"} placement="right">
            <button 
              onClick={toggleTheme}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all"
            >
              {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </Tippy>
          
          <Tippy content="New post" placement="right">
            <button 
              onClick={() => setIsNewBlogModalOpen(true)}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all"
            >
              <Plus className="w-5 h-5" />
            </button>
          </Tippy>
          
          <Tippy content="Posts inbox" placement="right">
            <button 
              onClick={onToggleDrawer}
              className={`p-2 rounded-lg transition-all ${
                isDrawerOpen 
                  ? 'bg-gray-100 dark:bg-gray-700' 
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <Inbox className="w-5 h-5" />
            </button>
          </Tippy>
        </div>
      </div>

      <NewBlogModal
        isOpen={isNewBlogModalOpen}
        onClose={() => setIsNewBlogModalOpen(false)}
        onGenerate={async () => {}}
      />
    </>
  );
};