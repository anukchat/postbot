import React from 'react';
import { Post } from '../../types';
import { useEditorStore } from '../../store/editorStore';

interface BlogListProps {
  blogs: Post[];
  onSelect: (post: Post) => void;
}

export const BlogList: React.FC<BlogListProps> = ({ blogs, onSelect }) => {

    console.log("Posts in BlogList:", blogs); // Add this for debugging

  return (
    <div className="overflow-auto">
      {blogs.map((post) => (
        <button
          key={post.id}
          onClick={() => onSelect(post)}
          className="w-full p-4 text-left hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          <h3 className="font-medium mb-1">{post.title}</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {new Date(post.updatedAt).toLocaleDateString()}
          </p>
        </button>
      ))}
    </div>
  );
}; 