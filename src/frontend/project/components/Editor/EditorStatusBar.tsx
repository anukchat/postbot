import React from 'react';
import { Post } from '../../types/editor';

interface EditorStatusBarProps {
  post: Post;
  content: string;
}

export const EditorStatusBar: React.FC<EditorStatusBarProps> = ({ post, content }) => {
  return (
    <div className="bg-white dark:bg-gray-800 p-4 text-sm text-gray-500">
      {content.split(' ').length -1} words • Last saved: {new Date(post.updatedAt).toLocaleString()}
    </div>
  );
};