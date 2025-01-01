import React, { useEffect, useRef } from 'react';
import { Tweet } from 'react-tweet';

interface TwitterEmbedProps {
  tweetId: string;
}

export const TwitterEmbed: React.FC<TwitterEmbedProps> = ({ tweetId }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    return () => {
      // Cleanup Twitter widget before unmounting
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
      // Remove any Twitter scripts
      const scripts = document.querySelectorAll('script[src*="twitter"]');
      scripts.forEach(script => script.remove());
    };
  }, [tweetId]);

  return (
    <div ref={containerRef} className="twitter-embed-container">
      <Tweet id={tweetId} />
    </div>
  );
};
