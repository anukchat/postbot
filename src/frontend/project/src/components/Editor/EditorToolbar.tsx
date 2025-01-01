import React, { useState } from 'react';
import { Save, FileDown, Send, FileUp, Sun, Moon, Plus, ChevronRight, ChevronLeft, Home } from 'lucide-react';
import { useEditorStore } from '../../store/editorStore';
import Tippy from '@tippyjs/react';
import 'tippy.js/dist/tippy.css';
import { PublishModal } from './PublishModal';

interface EditorToolbarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const EditorToolbar: React.FC<EditorToolbarProps> = ({ isCollapsed, onToggleCollapse }) => {
  const { savePost, publishPost, downloadMarkdown, toggleTheme, isDarkMode } = useEditorStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  return (
    <div className={`bg-white dark:bg-gray-800 p-2 border-b flex ${isCollapsed ? 'flex-col items-center' : 'items-center gap-2'}`}>
      <div className={`flex ${isCollapsed ? 'flex-col items-center' : 'items-center justify-between'} p-4`}>
        <Tippy content="Home">
          <a href="/" className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
            <Home className="w-5 h-5" />
          </a>
        </Tippy>
        <Tippy content="Toggle Theme">
          <button
            onClick={toggleTheme}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          >
            {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
        </Tippy>
        <Tippy content="New Post">
          <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
            <Plus className="w-5 h-5" />
          </button>
        </Tippy>
        <Tippy content={isCollapsed ? "Expand" : "Collapse"}>
          <button
            onClick={onToggleCollapse}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          >
            {isCollapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
          </button>
        </Tippy>
        <Tippy content="Save">
          <button
            onClick={savePost}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          >
            <Save className="w-5 h-5" />
          </button>
        </Tippy>
        <Tippy content="Download Markdown">
          <button
            onClick={downloadMarkdown}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          >
            <FileDown className="w-5 h-5" />
          </button>
        </Tippy>
        <Tippy content="Publish">
          <button
            onClick={publishPost}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          >
            <Send className="w-5 h-5" />
          </button>
          {/* <button onClick={() => setIsModalOpen(true)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
            <Send className="w-5 h-5" />
          </button> */}
        </Tippy>
        <PublishModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
        <Tippy content="Import">
          <button
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          >
            <FileUp className="w-5 h-5" />
          </button>
        </Tippy>
      </div>
    </div>
  );
};