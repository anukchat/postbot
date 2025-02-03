import React from 'react';
import { useEditorStore } from '../../store/editorStore';
import { EditorStatusBar } from './EditorStatusBar';
import { WysiwygEditor } from './WysiwygEditor';

interface MarkdownEditorProps {
  content: string;
  onChange: (newContent: string) => void;
  selectedTab: 'blog' | 'twitter' | 'linkedin';
}

export const MarkdownEditor: React.FC<MarkdownEditorProps> = ({ content, onChange }) => {
  const { currentPost } = useEditorStore();

  return (
    <>
      {!currentPost ? (
        <div className="flex items-center justify-center w-full h-full min-h-[50vh] sm:min-h-screen gap-2 p-4 text-center">
          <p className="text-gray-500 text-base sm:text-lg">
            Generate new or select existing post to edit
          </p>
        </div>
      ) : (
        <div className="flex flex-col h-full">
          <WysiwygEditor 
            content={content} 
            onChange={onChange}
            readOnly={currentPost?.status === 'Published'}
          />
          {currentPost && <EditorStatusBar post={currentPost} />}
        </div>
      )}
    </>
  );
};