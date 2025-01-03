import React, { useState, useEffect, useCallback } from 'react';
import { Dialog } from '@headlessui/react';
import { Twitter, Globe, X, Loader, Search, ChevronLeft, Grid2X2, LayoutList } from 'lucide-react';
import { Tweet } from 'react-tweet';
import { useEditorStore } from '../../store/editorStore';
import Masonry from 'react-masonry-css';
import api from '../../services/api';
import { Source } from '../../types';
import { LinkPreview as CustomLinkPreview } from '../Editor/LinkPreview';
import { useNavigate } from 'react-router-dom'; // Replace useRouter
import { SourceCard } from '../Sources/SourceCard';
import { GenerateLoader } from '../Editor/GenerateLoader';
import Tippy from '@tippyjs/react';
import MicrolinkCard from '@microlink/react';

const LOADING_MESSAGES = {
  blog: [
    "Analyzing the conten</div>t...",
    "Crafting an engaging narrative...",
    "Adding some personality...",
    "Making it readable and engaging...",
    "Almost there..."
  ],
  twitter: [
    "Distilling into tweet-sized wisdom...",
    "Finding the perfect hook...",
    "Making it tweet-worthy...",
  ],
  linkedin: [
    "Adding professional insights...",
    "Crafting for your network...",
    "Making it LinkedIn ready...",
  ]
};

const MASONRY_BREAKPOINTS = {
  default: 2,
  1100: 2,
  700: 1
};

interface SourceData {
  id: string;
  source_id: string;
  source_identifier: string;
  source_type: string;
  metadata?: any;
  created_at: string;
  has_blog: boolean;
  thread_id?: string;
  has_url: boolean;  // Changed from optional to required, defaults to false
}

type SourceType = 'twitter' | 'web';

interface NewBlogModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (tweetId: string) => Promise<void>;
}

interface SourceListResponse {
  items: Source[];
  total: number;
  page: number;
  size: number;
}

interface CustomUrlForm {
  url: string;
  isValid: boolean;
}

interface PreviewData {
  title?: string;
  description?: string;
  image?: string;
  siteName?: string;
  url: string;
}

export const NewBlogModal: React.FC<NewBlogModalProps> = ({ isOpen, onClose }) => {
  const [selectedSource, setSelectedSource] = useState<SourceType | null>(null);
  const [selectedIdentifier, setSelectedIdentifier] = useState(''); // Change this to store the unique ID
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchText, setSearchText] = useState('');
  const [sources, setSources] = useState<SourceData[]>([]);
  const [isGridView, setIsGridView] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const itemsPerPage = 10;
  const { fetchPosts } = useEditorStore();
  const [customUrl, setCustomUrl] = useState<CustomUrlForm>({ url: '', isValid: false });
  const [isCustomUrl, setIsCustomUrl] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const navigate = useNavigate(); // Replace router
  const [isGenerating, setIsGenerating] = useState(false); // Add new state for generation

  const fetchSources = async () => {
    if (!selectedSource) return;

    setIsLoading(true);
    try {
      const params = {
        type: selectedSource === 'twitter' ? 'twitter' : 'web_url',
        source_identifier: searchText || undefined,
        skip: (currentPage - 1) * itemsPerPage,
        limit: itemsPerPage
      };

      const response = await api.get<SourceListResponse>('/sources', { params });

      if (response.data) {
        const sourcesData = response.data.items.map(source => ({
          id: source.source_id,
          source_id: source.source_id,
          source_identifier: source.source_identifier,
          source_type: source.source_type,
          created_at: source.created_at,
          metadata: source.metadata,
          has_blog: source.has_blog,
          thread_id: source.thread_id,
          has_url: source.has_url
        }));
        
        setSources(sourcesData);
        setTotalItems(response.data.total);
      }
    } catch (err) {
      console.error('Failed to fetch sources:', err);
      setError('Failed to load sources');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSources();
  }, [selectedSource, searchText, currentPage]);

  const totalPages = Math.ceil(totalItems / itemsPerPage);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  // Add URL validation function
  const validateUrl = (url: string): boolean => {
    try {
      new URL(url);
      return true;
    } catch (e) {
      return false;
    }
  };

  // Handle custom URL input
  const handleCustomUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value;
    setCustomUrl({
      url,
      isValid: validateUrl(url)
    });
  };

  // Add loading message rotation
  useEffect(() => {
    if (!isLoading) return;

    const messages = LOADING_MESSAGES.blog;
    let currentIndex = 0;

    const interval = setInterval(() => {
      setLoadingMessage(messages[currentIndex]);
      currentIndex = (currentIndex + 1) % messages.length;
    }, 2000);

    return () => clearInterval(interval);
  }, [isLoading]);

  // Update handleGenerate to directly use the URL
  const handleGenerate = async () => {
    if (isCustomUrl) {
      if (!customUrl.isValid) {
        setError('Please enter a valid URL');
        return;
      }
      setIsGenerating(true); // Use generating state instead of loading
      try {
        const payload = {
          post_types: ["blog"],
          url: customUrl.url
        };
        await api.post('/content/generate', payload);
        await fetchPosts({}); // Refresh the posts list
        onClose();
      } catch (err) {
        console.error('Failed to generate blog:', err);
        setError('Failed to generate blog');
      } finally {
        setIsGenerating(false);
      }
      return;
    }

    if (!selectedIdentifier) {
      setError('Please select a source');
      return;
    }

    // Find the selected source data from sources array
    const sourceData = sources.find(source => getUniqueId(source) === selectedIdentifier);
    if (!sourceData) {
      setError('Selected source not found');
      return;
    }

    setIsGenerating(true); // Use generating state instead of loading
    
    try {
      const payload = {
      post_types: ["blog"],
      [selectedSource === 'twitter' ? 'tweet_id' : 'url']: sourceData.source_identifier
      };
      
      console.log('Generate payload:', payload);
      const response = await api.post('/content/generate', payload);
      
      // Wait longer to ensure backend processing is complete
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Force refresh posts with no cache
      await fetchPosts({ 
      forceRefresh: true,
      timestamp: new Date().getTime()
      
      })
      onClose();
      ;
      
    } catch (err) {
      console.error('Failed to generate blog:', err);
      setError('Failed to generate blog');
    } finally {
      setIsGenerating(false);
    }
  };

  const isValidUrl = (urlString: string): boolean => {
    try {
      return Boolean(new URL(urlString));
    } catch (e) {
      return false;
    }
  };

  // Remove the fetchLinkPreview function and urlPreviews state
  // Remove the existing renderSourceContent function and replace with this:
  
  const renderSourceContent = (source: Source) => {
    if (selectedSource === 'twitter') {
      return (
        <div className="flex justify-center p-4">
          <div className="w-full max-w-[400px]">
            <Tweet id={source.source_identifier} />
          </div>
        </div>
      );
    }

    // For web URLs, use MicrolinkCard with smaller size
    if (source.source_type === 'web_url' && source.source_identifier) {
      return (
        <div 
          className="cursor-pointer w-full overflow-hidden p-2" // Added padding
          onClick={() => setSelectedIdentifier(getUniqueId(source))}
        >
          <MicrolinkCard 
            url={source.source_identifier}
            contrast
            size="large" // Changed from large to small
            media={['image', 'logo']}
            mediaSize="contain" // Changed to contain to prevent zoom
            className="!rounded-lg !border !border-gray-200 dark:!border-gray-700 pointer-events-none !max-w-full !transform !scale-90" // Added scale down
            style={{ objectFit: 'contain' }} // Added object-fit contain
          />
        </div>
      );
    }

    return null;
  };

  const renderPagination = () => (
    <div className="flex items-center justify-between border-t border-gray-200 dark:border-gray-700 pt-4 mt-4">
      <button
        onClick={() => handlePageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className={`px-4 py-2 text-sm font-medium rounded ${
          currentPage === 1
            ? 'bg-gray-100 text-gray-400 dark:bg-gray-700 dark:text-gray-500'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
        }`}
      >
        Previous
      </button>
      <div className="text-sm text-gray-500">
        <span className="font-medium">{currentPage}</span>
        {' of '}
        <span className="font-medium">{totalPages || 1}</span>
        {' pages '}
        <span className="text-gray-400">
          ({totalItems} items)
        </span>
      </div>
      <button
        onClick={() => handlePageChange(currentPage + 1)}
        disabled={currentPage >= totalPages || totalItems <= itemsPerPage}
        className={`px-4 py-2 text-sm font-medium rounded ${
          currentPage >= totalPages || totalItems <= itemsPerPage
            ? 'bg-gray-100 text-gray-400 dark:bg-gray-700 dark:text-gray-500'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
        }`}
      >
        Next
      </button>
    </div>
  );

  // Reset pagination when changing source or search
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedSource, searchText]);

  // Update getUniqueId to be more robust
  const getUniqueId = (source: SourceData) => {
    return `${source.source_id || source.id}-${source.source_identifier}`;
  };

  // Add custom URL input section
  const renderCustomUrlInput = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <button
          onClick={() => setIsCustomUrl(false)}
          className="flex items-center gap-2 text-sm text-blue-500 hover:text-blue-600"
        >
          <ChevronLeft className="h-4 w-4" />
          Back to sources
        </button>
      </div>
      <div className="p-6 border rounded-lg dark:border-gray-700">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Enter URL
        </label>
        <input
          type="url"
          value={customUrl.url}
          onChange={handleCustomUrlChange}
          placeholder="https://example.com/article"
          className="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {customUrl.url && !customUrl.isValid && (
          <p className="mt-2 text-sm text-red-600">Please enter a valid URL</p>
        )}
      </div>
    </div>
  );

  // Update the source selection UI to include custom URL option
  const renderSourceSelection = () => (
    <div className="grid grid-cols-2 gap-4">
      <button
        onClick={() => setSelectedSource('twitter')}
        disabled={false} // Temporarily disabled
        className="group relative rounded-xl border border-gray-200 dark:border-gray-700 p-6 hover:border-blue-500 dark:hover:border-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <div className="flex flex-col items-center gap-4">
          <Twitter className="h-8 w-8 text-blue-400" />
          <span className="text-sm font-medium">From Twitter</span>
        </div>
      </button>
      <button
        onClick={() => setSelectedSource('web')}
        className="group relative rounded-xl border border-gray-200 dark:border-gray-700 p-6 hover:border-green-500 dark:hover:border-green-500 transition-colors"
      >
        <div className="flex flex-col items-center gap-4">
          <Globe className="h-8 w-8 text-green-500" />
          <span className="text-sm font-medium">From Web URL</span>
        </div>
      </button>
    </div>
  );

  // Add custom URL button to the source content section
  const renderSourceContentSection = () => (
    <div className="space-y-4">
      {/* Existing source header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => {
            setSelectedSource(null);
            setSelectedIdentifier('');
            setSources([]);
            setCurrentPage(0);
          }}
          className="flex items-center gap-2 text-sm text-blue-500 hover:text-blue-600"
        >
          <ChevronLeft className="h-4 w-4" />
          Back to sources
        </button>
        <div className="flex items-center gap-4">
          <button
            onClick={() => setIsGridView(!isGridView)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            title={isGridView ? "Switch to List View" : "Switch to Grid View"}
          >
            {isGridView ? <LayoutList className="w-4 h-4" /> : <Grid2X2 className="w-4 h-4" />}
          </button>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder={`Search ${selectedSource === 'twitter' ? 'tweets' : 'URLs'}...`}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              className="pl-9 pr-4 py-2 w-72 rounded-full border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            onClick={() => setIsCustomUrl(true)}
            disabled={selectedSource === 'twitter'}
            className="px-4 py-2 text-sm font-medium text-blue-500 border border-blue-500 rounded-lg hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {selectedSource === 'twitter' ? 'Add Twitter ID (Coming Soon)' : 'Add Custom URL'}
          </button>
        </div>
      </div>
      <div className="max-h-[60vh] overflow-y-auto px-4 py-2">
        {isLoading && !isGenerating ? ( // Only show normal loader when not generating
          <div className="flex justify-center py-8">
            <Loader className="h-6 w-6 animate-spin text-blue-500" />
          </div>
        ) : sources.length > 0 ? (
          <>
            {isGridView ? (
              <Masonry
                breakpointCols={MASONRY_BREAKPOINTS}
                className="flex w-auto -ml-4" // Add negative margin to offset column gap
                columnClassName="pl-4" // Add padding to create gap between columns
              >
                {sources.map((source) => (
                  <SourceCard
                    key={getUniqueId(source)}
                    source={source}
                    isSelected={selectedIdentifier === getUniqueId(source)}
                    onSelect={() => setSelectedIdentifier(getUniqueId(source))}
                    hasExistingBlog={source.has_blog} // Use the has_blog property from the API
                    existingBlogId={source.thread_id} // Use thread_id from the API
                    onViewBlog={handleViewBlog}
                    className="mb-4"  // Add bottom margin for vertical spacing
                  >
                    {renderSourceContent(source)}
                  </SourceCard>
                ))}
              </Masonry>
            ) : (
              <div className="flex flex-col gap-4">
                {sources.map((source) => (
                  <SourceCard
                    key={getUniqueId(source)}
                    source={source}
                    isSelected={selectedIdentifier === getUniqueId(source)}
                    onSelect={() => setSelectedIdentifier(getUniqueId(source))}
                    hasExistingBlog={Boolean(source.has_blog)}
                    existingBlogId={source.thread_id}
                    onViewBlog={handleViewBlog}
                    className="mb-4"
                  >
                    {renderSourceContent(source)}
                  </SourceCard>
                ))}
              </div>
            )}
            {renderPagination()}
          </>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No sources found
          </div>
        )}
      </div>
    </div>
  );

  // Add handler for viewing blog
  const handleViewBlog = (blogId: string) => {
    navigate(`/editor/${blogId}`);
    onClose();
  };

  // Update the isGenerateDisabled function with null checks
  const isGenerateDisabled = useCallback((source?: SourceData) => {
    // For custom URL case
    if (isCustomUrl) {
      return !customUrl.isValid || isGenerating;
    }
    
    // For regular sources
    if (!source) return true;
    
    return isGenerating || 
           !selectedIdentifier || 
           (source.source_type === 'twitter' && !source.has_url);
  }, [isGenerating, selectedIdentifier, isCustomUrl, customUrl.isValid]);

  const getGenerateButtonTooltip = useCallback((source?: SourceData) => {
    // For custom URL case
    if (isCustomUrl) {
      if (!customUrl.isValid) return 'Please enter a valid URL';
      if (isGenerating) return 'Generation in progress...';
      return 'Generate Blog';
    }
    
    // For regular sources
    if (isGenerating) return 'Generation in progress...';
    if (!selectedIdentifier) return 'Please select a source';
    if (source?.source_type === 'twitter' && !source.has_url) {
      return 'This tweet has no URLs for content generation';
    }
    return 'Generate Blog';
  }, [isGenerating, selectedIdentifier, isCustomUrl, customUrl.isValid]);

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      {/* Dark overlay */}
      <div className="fixed inset-0 bg-black/30 backdrop-blur-sm" aria-hidden="true" />

      {/* Update container z-index */}
      <div className="fixed inset-0 overflow-y-auto z-[50]">
        <div className="flex min-h-full items-center justify-center p-4">
          <Dialog.Panel className="w-full max-w-4xl rounded-xl bg-white dark:bg-gray-800 shadow-xl transition-all relative">
            {/* Modal header */}
            <div className="border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
              <Dialog.Title className="text-lg font-semibold text-gray-900 dark:text-white">
                Create New Blog Post
              </Dialog.Title>
              <button 
                onClick={onClose}
                className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Modal content */}
            <div className="px-6 py-4">
              {error && (
                <div className="mb-4 p-4 bg-red-50 text-red-600 rounded-lg">
                  {error}
                </div>
              )}

              {!selectedSource && renderSourceSelection()}
              {selectedSource && !isCustomUrl && renderSourceContentSection()}
              {selectedSource && isCustomUrl && renderCustomUrlInput()}
            </div>

            {/* Modal footer */}
            {selectedSource && (
              <div className="border-t border-gray-200 dark:border-gray-700 px-6 py-4 flex justify-end gap-3">
                <button
                  onClick={onClose}
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-lg"
                >
                  Cancel
                </button>
                <Tippy content={getGenerateButtonTooltip(
                  isCustomUrl ? undefined : sources.find(s => getUniqueId(s) === selectedIdentifier)
                )}>
                  <button
                    onClick={handleGenerate}
                    disabled={isCustomUrl 
                      ? !customUrl.isValid || isGenerating
                      : isGenerateDisabled(sources.find(s => getUniqueId(s) === selectedIdentifier))
                    }
                    className={`px-4 py-2 text-sm font-medium text-white bg-blue-500 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2`}
                  >
                    Generate Blog
                  </button>
                </Tippy>
              </div>
            )}
          </Dialog.Panel>
        </div>
      </div>
      {isGenerating && (
        <GenerateLoader platform={'blog'} />
      )}
    </Dialog>
  );
};
