import React, { useState } from 'react';
import { useEditorStore } from '../../store/editorStore';
import { Home, Inbox, Menu, Settings, Sun, Moon, AlignJustify, LayoutTemplate, Shield } from 'lucide-react';
import { NewBlogModal } from '../Modals/NewBlogModal';
import { Dialog } from '@headlessui/react';
import { TemplateManagement } from '../Templates/TemplateManagement';
import Tippy from '@tippyjs/react';
import ReactDOM from 'react-dom';
import { Link, useNavigate, useLocation } from 'react-router-dom';

interface FloatingNavProps {
  onToggleDrawer: () => void;
  isDrawerOpen: boolean;
}

export const FloatingNav: React.FC<FloatingNavProps> = ({ onToggleDrawer, isDrawerOpen }) => {
  const { toggleTheme, isDarkMode, setCurrentPost } = useEditorStore();
  const [isNewBlogModalOpen, setIsNewBlogModalOpen] = useState(false);
  const [isTemplateManagementOpen, setIsTemplateManagementOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleHomeClick = () => {
    // Clear current post and navigate to templates view
    setCurrentPost(null);
    if (location.pathname !== '/dashboard') {
      navigate('/dashboard');
    }
  };

  return (
    <>
      <div className="fixed left-0 top-0 bottom-0 w-16 bg-white dark:bg-gray-800 z-50 border-r border-gray-200 dark:border-gray-700 flex flex-col items-center py-4 gap-2">
        <div className="h-full flex flex-col justify-between">
          <div className="flex flex-col items-center gap-4 pt-4">
            {/* Logo */}
            <Link to="/" className="flex items-center mb-4">
              <img
                src="/assets/riteup logo svg.svg"
                alt="RiteUp Logo"
                className="h-10 w-auto transition-transform duration-300 hover:scale-105"
              />
            </Link>
            {/* Home - Updated with new handler */}
            <Tippy content="Home" placement="right">
              <button 
                onClick={handleHomeClick} 
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                <Home className="w-5 h-5" />
              </button>
            </Tippy>
            <Tippy content="Inbox" placement="right">
              <button
                onClick={onToggleDrawer}
                className={`p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors ${isDrawerOpen ? 'bg-gray-100 dark:bg-gray-700' : ''}`}
              >
                <Inbox className="w-5 h-5" />
              </button>
            </Tippy>
          </div>
          <div className="flex flex-col items-center gap-4">
            <Tippy content={isDarkMode ? "Light mode" : "Dark mode"} placement="right">
              <button
                onClick={toggleTheme}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>
            </Tippy>
            
            <Tippy content="Admin Panel" placement="right">
              <button 
                onClick={() => navigate('/admin')} 
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                <Shield className="w-5 h-5" />
              </button>
            </Tippy>
            
            <Tippy content="Settings" placement="right">
              <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                <Settings className="w-5 h-5" />
              </button>
            </Tippy>
          </div>
        </div>
      </div>

      {isNewBlogModalOpen && ReactDOM.createPortal(
        <NewBlogModal
          isOpen={isNewBlogModalOpen}
          onClose={() => setIsNewBlogModalOpen(false)}
          onGenerate={async () => {}}
        />,
        document.body
      )}

      {isTemplateManagementOpen && ReactDOM.createPortal(
        <Dialog 
          open={isTemplateManagementOpen} 
          onClose={() => setIsTemplateManagementOpen(false)}
          className="relative z-[1000]"
        >
          <div className="fixed inset-0 bg-black/30 backdrop-blur-sm z-[1001]" aria-hidden="true" />
          <div className="fixed inset-0 overflow-y-auto z-[1002]">
            <div className="flex min-h-full items-center justify-center p-4">
              <Dialog.Panel className="relative w-[800px] sm:w-[900px] max-h-[90vh] bg-white dark:bg-gray-800 shadow-2xl rounded-lg">
                <TemplateManagement/>
              </Dialog.Panel>
            </div>
          </div>
        </Dialog>,
        document.body
      )}
    </>
  );
};