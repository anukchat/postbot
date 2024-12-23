import React from 'react';
import { Save, FileDown, Send, FileUp, Sun, Moon, Plus, ChevronRight, ChevronLeft, XCircle } from 'lucide-react';
import { useEditorStore } from '../../store/editorStore';
import Tippy from '@tippyjs/react';
import 'tippy.js/dist/tippy.css';

interface EditorToolbarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const EditorToolbar: React.FC<EditorToolbarProps> = ({ isCollapsed, onToggleCollapse }) => {
  const { savePost, publishPost, rejectPost, downloadMarkdown, toggleTheme, isDarkMode, currentPost, isContentUpdated } = useEditorStore();

  const saveIconColor = isContentUpdated ? 'text-green-500' : '';
  const publishIconColor = currentPost?.status && ['Published', 'Rejected'].includes(currentPost.status) ? 'text-gray-300' : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-green-500 ';
  const rejectIconColor = currentPost?.status =='Rejected' ? 'text-gray-300' : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-red-500 ';

  const isDisabled = currentPost?.status === 'Published' || currentPost?.status === 'Rejected';

  return (
    <div className={`bg-white dark:bg-gray-800 p-2 border-b flex ${isCollapsed ? 'flex-col items-center' : 'items-center gap-2'}`}>
      <div className={`flex ${isCollapsed ? 'flex-col items-center' : 'items-center justify-between'} p-4`}>
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
        <Tippy content="Save">
          <button
            onClick={savePost}
            className={`p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded ${saveIconColor}`}
            // disabled={isDisabled}
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
            className={`p-2 rounded ${publishIconColor}`}
            disabled={isDisabled}
          >
            <Send className="w-5 h-5" />
          </button>
        </Tippy>
        <Tippy content="Reject">
          <button
            onClick={rejectPost}
            className={`p-2 rounded ${rejectIconColor}`}
            disabled={currentPost?.status === 'Rejected'}
          >
            <XCircle className="w-5 h-5" />
          </button>
        </Tippy>
        {/* <Tippy content="Import">
          <button
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          >
            <FileUp className="w-5 h-5" />
          </button>
        </Tippy> */}
        <Tippy content={isCollapsed ? "Expand" : "Collapse"}>
          <button
            onClick={onToggleCollapse}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          >
            {isCollapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
          </button>
        </Tippy>
      </div>
    </div>
  );
};