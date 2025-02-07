import React from 'react';
import { Post } from '../../types';

interface EditorStatusBarProps {
  post: Post;
}

export const EditorStatusBar: React.FC<EditorStatusBarProps> = ({ post }) => {
  return (
    <div className="bg-white dark:bg-gray-800 p-4 border-t text-sm text-gray-500">
      {post.content.split(' ').length} words • Last saved: {new Date(post.updatedAt).toLocaleString()}
    </div>
  );
};