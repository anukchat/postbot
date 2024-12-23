import React, { useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { useEditorStore } from '../../store/editorStore';
import { Post } from '../../types';

interface EditorContentProps {
  post: Post;
}

export const EditorContent: React.FC<EditorContentProps> = ({ post }) => {
  const { setCurrentPost } = useEditorStore();

  const handleChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setCurrentPost({
      ...post,
      content: e.target.value,
      updatedAt: new Date().toISOString(),
    });
  }, [post, setCurrentPost]);

  return (
    <div className="flex-1 grid grid-cols-2 gap-4 p-4 overflow-hidden">
      <textarea
        value={post.content}
        onChange={handleChange}
        className="h-full p-4 bg-white dark:bg-gray-800 border rounded resize-none focus:outline-none focus:ring-2"
        placeholder="Write your markdown here..."
      />
      <div className="h-full p-4 bg-white dark:bg-gray-800 border rounded overflow-auto prose dark:prose-invert max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw]}
        >
          {post.content}
        </ReactMarkdown>
      </div>
    </div>
  );
};