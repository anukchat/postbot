import React from 'react';
import { FileText, Twitter, Link, Layout, Info } from 'lucide-react';
import Tippy from '@tippyjs/react';
import { useEditorStore } from '../../store/editorStore';

interface FloatingTabsProps {
  selectedTab: 'blog' | 'twitter' | 'linkedin';
  onTabChange: (tab: 'blog' | 'twitter' | 'linkedin') => void;
  onViewChange: (view: 'canvas' | 'details') => void;
  currentView: 'editor' | 'canvas' | 'details';
}

export const FloatingTabs: React.FC<FloatingTabsProps> = ({
  selectedTab,
  onTabChange,
  onViewChange,
  currentView
}) => {
  return (
    <div className="fixed right-4 top-1/2 -translate-y-1/2 z-[60]">
      <div className="flex flex-col gap-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-2">
        <Tippy content="Blog" placement="left">
          <button
            onClick={() => onTabChange('blog')}
            className={`p-2 rounded-md ${selectedTab === 'blog' ? 'bg-blue-100 dark:bg-blue-800' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}
          >
            <FileText className="w-4 h-4" />
          </button>
        </Tippy>
        <Tippy content="Twitter" placement="left">
          <button
            onClick={() => onTabChange('twitter')}
            className={`p-2 rounded-md ${selectedTab === 'twitter' ? 'bg-blue-100 dark:bg-blue-800' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}
          >
            <Twitter className="w-4 h-4" />
          </button>
        </Tippy>
        <Tippy content="LinkedIn" placement="left">
          <button
            onClick={() => onTabChange('linkedin')}
            className={`p-2 rounded-md ${selectedTab === 'linkedin' ? 'bg-blue-100 dark:bg-blue-800' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}
          >
            <Link className="w-4 h-4" />
          </button>
        </Tippy>
        <div className="w-full h-px bg-gray-200 dark:bg-gray-700 my-1" />
        <Tippy content="Canvas View" placement="left">
          <button
            onClick={() => onViewChange('canvas')}
            className={`p-2 rounded-md ${currentView === 'canvas' ? 'bg-blue-100 dark:bg-blue-800' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}
          >
            <Layout className="w-4 h-4" />
          </button>
        </Tippy>
        <Tippy content="Post Details" placement="left">
          <button
            onClick={() => onViewChange('details')}
            className={`p-2 rounded-md ${currentView === 'details' ? 'bg-blue-100 dark:bg-blue-800' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}
          >
            <Info className="w-4 h-4" />
          </button>
        </Tippy>
      </div>
    </div>
  );
};
