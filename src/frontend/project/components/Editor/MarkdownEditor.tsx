import React from 'react';
import { useEditorStore } from '../../store/editorStore';
import { EditorStatusBar } from './EditorStatusBar';
import { WysiwygEditor } from './WysiwygEditor';
import { ContentLoader } from '../common/ContentLoader';

interface MarkdownEditorProps {
  content: string;
  onChange: (newContent: string) => void;
  selectedTab: 'blog' | 'twitter' | 'linkedin';
}

export const MarkdownEditor: React.FC<MarkdownEditorProps> = ({ content, onChange, selectedTab }) => {
  const { currentPost, isLoading } = useEditorStore();

  if (!currentPost) {
    return (
      <div className="flex items-center justify-center w-full h-full min-h-[50vh] sm:min-h-screen gap-2 p-4 text-center">
        <p className="text-gray-500 text-base sm:text-lg">
          Generate new or select existing post to edit
        </p>
      </div>
    );
  }

  if (isLoading) {
    return <ContentLoader />;
  }

  return (
    <div className="flex flex-col h-full relative">
      <WysiwygEditor 
      content={content} 
      onChange={onChange}
      readOnly={currentPost?.status === 'Published'}
      />
      {/* Status bar with full width at bottom */}
      <div className="absolute bottom-0 left-0 right-0 bg-white border-t">
        <EditorStatusBar post={currentPost} />
      </div>
    </div>
  );
};