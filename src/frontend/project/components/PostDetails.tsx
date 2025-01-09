import React from 'react';
import { useEditorStore } from '../store/editorStore';

export const PostDetails: React.FC = () => {
  const { currentPost } = useEditorStore();

  if (!currentPost) {
    return (
      <div className="flex items-center justify-center min-h-[50vh] text-gray-500">
        No post selected
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 md:p-8 max-w-4xl mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        <div className="space-y-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
            <h3 className="text-lg font-medium mb-2">Basic Info</h3>
            <div className="space-y-2">
              <p className="text-sm sm:text-base">
                <span className="font-medium">Title:</span> {currentPost.title}
              </p>
              <p className="text-sm sm:text-base">
                <span className="font-medium">Status:</span> {currentPost.status}
              </p>
              <p className="text-sm sm:text-base">
                <span className="font-medium">Created:</span>{' '}
                {new Date(currentPost.createdAt).toLocaleDateString()}
              </p>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
            <h3 className="text-lg font-medium mb-2">Tags</h3>
            <div className="flex flex-wrap gap-2">
              {currentPost.tags.map((tag, index) => (
                <span
                  key={index}
                  className="px-2 py-1 text-xs sm:text-sm bg-gray-100 dark:bg-gray-700 rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
            <h3 className="text-lg font-medium mb-2">URLs</h3>
            <div className="space-y-2 max-h-[200px] overflow-y-auto">
              {currentPost.urls?.map((url, index) => (
                <a
                  key={index}
                  href={url.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block text-blue-500 hover:underline text-sm sm:text-base truncate"
                >
                  {url.url}
                </a>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
            <h3 className="text-lg font-medium mb-2">Media</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {currentPost.media?.map((item, index) => (
                <div key={index} className="relative aspect-video">
                  {item.type === 'image' ? (
                    <img
                      src={item.url}
                      alt={item.alt_text || ''}
                      className="rounded object-cover w-full h-full"
                    />
                  ) : (
                    <video
                      src={item.url}
                      controls
                      className="rounded w-full h-full"
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
