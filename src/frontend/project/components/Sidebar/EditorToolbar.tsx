import React, { useState } from 'react';
import { Save, FileDown, Send, Sun, Moon, Plus, XCircle, Home, X } from 'lucide-react';
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

  const renderToolbarItems = () => {
    const items = [
      { icon: <Home className="w-5 h-5" />, tooltip: "Home", action: () => window.location.href = "/" },
      { icon: isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />, tooltip: "Toggle Theme", action: toggleTheme },
      { icon: <Plus className="w-5 h-5" />, tooltip: "New Post", action: () => setIsNewBlogModalOpen(true) },
      // { icon: <Save className="w-5 h-5" />, tooltip: "Save", action: savePost, className: saveIconColor },
      // { icon: <FileDown className="w-5 h-5" />, tooltip: "Download", action: downloadMarkdown },
      // { icon: <Send className="w-5 h-5" />, tooltip: "Publish", action: publishPost, className: publishIconColor, disabled: isDisabled },
      // { icon: <XCircle className="w-5 h-5" />, tooltip: "Reject", action: rejectPost, className: rejectIconColor, disabled: currentPost?.status === 'Rejected' }
    ];

    return items.map((item, index) => (
      <Tippy key={index} content={item.tooltip} placement={isCollapsed ? "right" : "bottom"}>
        <button
          onClick={item.action}
          // disabled={item.disabled}
          className={`p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded }`}
        >
          {item.icon}
        </button>
      </Tippy>
    ));
  };

  return (
    <>
      <div className={`bg-white dark:bg-gray-800 ${
        isCollapsed 
          ? 'fixed left-0 top-0 h-full w-16 flex flex-col items-center py-16 gap-4 dark:border-gray-700 border-r'
          : 'w-full border-b dark:border-gray-700 '
      }`}>
        {!isCollapsed && (
          <div className="p-2 sm:p-3 md:p-4 flex justify-between items-center w-full">
            <div className="flex items-center gap-2 p-2">
              {renderToolbarItems()}
              <button
              onClick={onToggleCollapse}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            >
              {/* <X className="w-6 h-6" /> */}
            </button>
            </div>
          </div>
        )
        }
        {isCollapsed && (
          <div className="flex flex-col items-center gap-4">
            {renderToolbarItems()}
          </div>
        )}
      </div>

      <NewBlogModal
        isOpen={isNewBlogModalOpen}
        onClose={() => setIsNewBlogModalOpen(false)}
        onGenerate={handleGenerateBlog}
      />
    </>
  );
};