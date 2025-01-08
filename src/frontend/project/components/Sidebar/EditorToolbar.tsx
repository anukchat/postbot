import React, { useState } from 'react';
import { Save, FileDown, Send, Sun, Moon, Plus, ChevronRight, ChevronLeft, XCircle, Home } from 'lucide-react';
import { useEditorStore } from '../../store/editorStore';
import Tippy from '@tippyjs/react';
import 'tippy.js/dist/tippy.css';
import { NewBlogModal } from '../Modals/NewBlogModal';
import { toast } from 'react-hot-toast';
import api from '../../services/api';

interface EditorToolbarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const EditorToolbar: React.FC<EditorToolbarProps> = ({ isCollapsed, onToggleCollapse }) => {
  const { savePost, publishPost, rejectPost, downloadMarkdown, toggleTheme, isDarkMode, currentPost, isContentUpdated, fetchPosts } = useEditorStore();
  const [isNewBlogModalOpen, setIsNewBlogModalOpen] = useState(false);
  const saveIconColor = isContentUpdated ? 'text-green-500' : '';
  const publishIconColor = currentPost?.status && ['Published', 'Rejected'].includes(currentPost.status) ? 'text-gray-300' : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-green-500 ';
  const rejectIconColor = currentPost?.status =='Rejected' ? 'text-gray-300' : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-red-500 ';

  const isDisabled = currentPost?.status === 'Published' || currentPost?.status === 'Rejected';

  const handleGenerateBlog = async (tweetId: string) => {
    try {
      await api.post('/blogs/generate', {
        tweet_id: tweetId
      });
      
      toast.success('Blog generated successfully!');
      
      // Refresh the posts list
      await fetchPosts({}, 0, 10);
      
    } catch (error) {
      toast.error('Failed to generate blog');
      throw error;
    }
  };

  return (
    <>
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
            <button 
              onClick={() => setIsNewBlogModalOpen(true)}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            >
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

      <NewBlogModal
        isOpen={isNewBlogModalOpen}
        onClose={() => setIsNewBlogModalOpen(false)}
        onGenerate={handleGenerateBlog}
      />
    </>
  );
};