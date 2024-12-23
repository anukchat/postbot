import React from 'react';
import { useEditorStore } from '../store/editorStore';

export const PostDetails: React.FC = () => {
  const { currentPost } = useEditorStore();

  if (!currentPost) {
    return <div className="p-4">No post selected</div>;
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard');
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">{currentPost.title}</h2>
      <p className="mb-2"><strong>Status:</strong> {currentPost.status}</p>
      <p className="mb-2"><strong>Created At:</strong> {new Date(currentPost.createdAt).toLocaleString()}</p>
      <p className="mb-2"><strong>Updated At:</strong> {new Date(currentPost.updatedAt).toLocaleString()}</p>
      <p className="mb-2"><strong>Tags:</strong> {currentPost.tags.join(', ')}</p>
      <button onClick={() => copyToClipboard(currentPost.tags.join(', '))} className="mb-2 bg-blue-500 text-white px-4 py-2 rounded">Copy Tags</button>
      <p className="mb-2"><strong>URLs:</strong></p>
      <ul className="mb-2">
        {currentPost.urls?.map((url, index) => (
          <li key={index}>
            <a href={url.original_url} target="_blank" rel="noopener noreferrer">{url.original_url}</a>
          </li>
        ))}
      </ul>
      <button onClick={() => copyToClipboard(currentPost.urls?.map(url => url.original_url).join(', ') || '')} className="mb-2 bg-blue-500 text-white px-4 py-2 rounded">Copy URLs</button>
      <p className="mb-2"><strong>Media:</strong></p>
      <ul className="mb-2">
        {currentPost.media?.map((media, index) => (
          <li key={index}>
            <a href={media.original_url} target="_blank" rel="noopener noreferrer">{media.original_url}</a>
          </li>
        ))}
      </ul>
      <button onClick={() => copyToClipboard(currentPost.media?.map(media => media.original_url).join(', ') || '')} className="mb-2 bg-blue-500 text-white px-4 py-2 rounded">Copy Media</button>
      {currentPost.tweet && (
        <div className="mt-4">
          <h3 className="text-lg font-semibold mb-2">Tweet Details</h3>
          <p className="mb-2"><strong>Tweet ID:</strong> {currentPost.tweet.tweet_id}</p>
          <p className="mb-2"><strong>Full Text:</strong> {currentPost.tweet.full_text}</p>
          <p className="mb-2"><strong>Created At:</strong> {new Date(currentPost.tweet.created_at).toLocaleString()}</p>
          <p className="mb-2"><strong>Screen Name:</strong> {currentPost.tweet.screen_name}</p>
        </div>
      )}
    </div>
  );
};
