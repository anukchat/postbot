import React, { useEffect, useState } from 'react';
import { Url } from '../../types';
import { Globe, Link as LinkIcon, Loader } from 'lucide-react';
import api from '../../services/api';
import { getLinkPreviewFromCache, setLinkPreviewInCache } from '../../utils/cache';

interface LinkPreviewProps {
  url: Url;
  onSelect: (url: Url) => void;
}

interface PreviewData {
  title?: string;
  description?: string;
  image?: string;
  force_title?: string;
  absolute_image?: string;
  url: string;
}

export const LinkPreview: React.FC<LinkPreviewProps> = ({ url, onSelect }) => {
  const [previewData, setPreviewData] = useState<PreviewData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const isValidUrl = (urlString: string): boolean => {
    try {
      new URL(urlString);
      return true;
    } catch (e) {
      return false;
    }
  };

  useEffect(() => {
    const fetchPreview = async () => {
      if (!url.url || !isValidUrl(url.url)) {
        setError('Invalid URL');
        return;
      }

      // Try to get from cache first
      const cached = getLinkPreviewFromCache(url.url);
      if (cached) {
        setPreviewData(cached);
        return;
      }

      try {
        setIsLoading(true);
        const response = await api.get('/api/link-preview', {
          params: { url: url.url }
        });
        const data = response.data.data;
        setPreviewData(data);
        setLinkPreviewInCache(url.url, data);
        setError('');
      } catch (err) {
        console.error('Failed to fetch preview:', err);
        setError('Error loading preview');
      } finally {
        setIsLoading(false);
      }
    };

    if (url.url) {
      // Show immediate basic preview
      setPreviewData({
        title: url.domain || new URL(url.url).hostname,
        description: '',
        url: url.url
      });
      
      // Then fetch full preview
      fetchPreview();
    }
  }, [url.url]);

  // Handle invalid URL by returning null instead of error UI
  if (!url.url || !isValidUrl(url.url)) {
    return null;
  }

  // Immediate preview while loading
  return (
    <div 
      className="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-4 rounded-lg border dark:border-gray-700 transition-colors"
      onClick={() => onSelect(url)}
    >
      <div className="flex gap-4">
        <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded flex items-center justify-center flex-shrink-0">
          {isLoading ? (
            <Loader className="w-6 h-6 animate-spin text-gray-400" />
          ) : previewData?.image ? (
            <img 
              src={previewData.absolute_image || previewData.image} 
              alt={previewData.title || ''}
              className="w-full h-full object-cover rounded"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
              }}
            />
          ) : (
            <Globe className="w-8 h-8 text-gray-400" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-medium mb-1 truncate">
            {previewData?.force_title || previewData?.title || url.url}
          </h3>
          {previewData?.description && !isLoading && (
            <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-2">
              {previewData.description}
            </p>
          )}
          <div className="flex items-center text-xs text-gray-400">
            <LinkIcon className="w-3 h-3 mr-1" />
            <span className="truncate">{url.domain || new URL(url.url).hostname}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
