import React, { useMemo } from 'react';
import { useEditorStore } from '../../store/editorStore';
import { EditorStatusBar } from './EditorStatusBar';
import { WysiwygEditor } from './WysiwygEditor';
import { ContentLoader } from '../common/ContentLoader';

interface MarkdownEditorProps {
  content: string;
  onChange: (newContent: string) => void;
  selectedTab: 'blog' | 'twitter' | 'linkedin';
}

export const MarkdownEditor: React.FC<MarkdownEditorProps> = React.memo(({ content, onChange, selectedTab }) => {
  const currentPost = useEditorStore(state => state.currentPost);
  const isContentLoading = useEditorStore(state => 
    state.isLoading && state.currentPost?.id === state.posts.find(p => p.id === state.currentPost?.id)?.id
  );

  const editorContent = useMemo(() => content, [content]);

  if (!currentPost) {
    return (
      <div className="flex items-center justify-center w-full h-full min-h-[50vh] sm:min-h-screen gap-2 p-4 text-center">
        <p className="text-gray-500 text-base sm:text-lg">
          Generate new or select existing post to edit
        </p>
      </div>
    );
  }

  if (isContentLoading) {
    return <ContentLoader />;
  }

  return (
    <div className="flex flex-col h-full relative">
      <WysiwygEditor 
        content={editorContent} 
        onChange={onChange}
        readOnly={currentPost?.status === 'Published'}
      />
      <div className="absolute bottom-0 left-0 right-0 bg-white border-t">
        <EditorStatusBar post={currentPost} />
      </div>
    </div>
  );
});

MarkdownEditor.displayName = 'MarkdownEditor';