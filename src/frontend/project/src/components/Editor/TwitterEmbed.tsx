import React, { useEffect } from 'react';

interface TwitterEmbedProps {
  tweetId: string;
}

export const TwitterEmbed: React.FC<TwitterEmbedProps> = ({ tweetId }) => {
  useEffect(() => {
    // Load Twitter widget script
    const script = document.createElement('script');
    script.src = 'https://platform.twitter.com/widgets.js';
    script.async = true;
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  return (
    <blockquote className="twitter-tweet">
      <a href={`https://twitter.com/user/status/${tweetId}`}></a>
    </blockquote>
  );
};
