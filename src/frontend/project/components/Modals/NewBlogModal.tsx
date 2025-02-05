import React, { useState, useEffect, useCallback } from 'react';
import { Dialog } from '@headlessui/react';
import { Twitter, Globe, X, Loader, Search, ChevronLeft, Grid2X2, LayoutList, MessageCircle, Loader2 } from 'lucide-react';
import { Tweet } from 'react-tweet';
import { useEditorStore } from '../../store/editorStore';
import Masonry from 'react-masonry-css';
import api from '../../services/api';
import { Source } from '../../types';
import { useNavigate } from 'react-router-dom'; // Replace useRouter
import { SourceCard } from '../Sources/SourceCard';
import { GenerateLoader } from '../Editor/GenerateLoader';
import Tippy from '@tippyjs/react';
import MicrolinkCard from '@microlink/react';
import { toast } from 'react-hot-toast';
import Select from 'react-select';

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

type SourceType = 'twitter' | 'web' | 'topic' | 'reddit';

// Add interface for topic form
interface TopicForm {
  topic: string;
  isValid: boolean;
}

// Add interface for Reddit form similar to TopicForm
interface RedditForm {
  query: string;
  isValid: boolean;
  subreddit: string | null;
}

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
  const { fetchPosts, redditTrendingTopics, fetchRedditTrending } = useEditorStore();
  const [customUrl, setCustomUrl] = useState<CustomUrlForm>({ url: '', isValid: false });
  const [isCustomUrl, setIsCustomUrl] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const navigate = useNavigate(); // Replace router
  const [isGenerating, setIsGenerating] = useState(false); // Add new state for generation
  // Add new state for topic
  const [customTopic, setCustomTopic] = useState<TopicForm>({ topic: '', isValid: false });
  const [isCustomTopic, setIsCustomTopic] = useState(false);
  const [trendingTopics] = useState([
    'AI and Machine Learning trends 2024',
    'Web Development Best Practices',
    'Cloud Computing Solutions',
    'Cybersecurity Essentials'
  ]);
  // Add new state for Reddit search
  const [redditSearch, setRedditSearch] = useState<RedditForm>({ 
    query: '', 
    isValid: false,
    subreddit: null 
  });
  const [isRedditSearch, setIsRedditSearch] = useState(false);
  const [trendingRedditTopics] = useState([
    'Programming',
    'Technology',
    'WebDev',
    'ArtificialIntelligence',
    'MachineLearning',
    'LocalLLaMA',
    'LocalLLM',
    'AI_Agents',
    'deeplearning',
    'generativeAI',
    'PromptEngineering',
    'accelerate',
    'artificial',
    'automate',
    `singularity`
  ]);
  const [selectedSubreddit, setSelectedSubreddit] = useState<string | null>(null);
  const [isLoadingTrending, setIsLoadingTrending] = useState(false);
  const [trendingPage, setTrendingPage] = useState(1);
  const TRENDING_PER_PAGE = 6;

  // Update fetchSources to handle Reddit search
  const fetchSources = async () => {
    if (!selectedSource) return;

    if (selectedSource === 'reddit' && !redditSearch.query) return;

    setIsLoading(true);
    try {
      const params = {
        type: selectedSource === 'twitter' 
          ? 'twitter' 
          : selectedSource === 'reddit'
            ? 'reddit'
            : 'web_url',
        source_identifier: selectedSource === 'reddit' ? redditSearch.query : searchText || undefined,
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

  // Add effect to trigger search when Reddit query changes
  useEffect(() => {
    if (selectedSource === 'reddit' && redditSearch.isValid) {
      fetchSources();
    }
  }, [redditSearch.query]);

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

  // Add topic validation
  const validateTopic = (topic: string): boolean => {
    return topic.length >= 3; // Minimum 3 characters
  };

  // Handle topic input change
  const handleTopicChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const topic = e.target.value;
    setCustomTopic({
      topic,
      isValid: validateTopic(topic)
    });
  };

  // Add Reddit validation similar to topic validation
  const validateRedditSearch = (query: string): boolean => {
    return query.length >= 3;
  };

  // Add handler for Reddit search input
  const handleRedditSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setRedditSearch({
      query,
      isValid: validateRedditSearch(query),
      subreddit: selectedSubreddit
    });
  };

  // Add handler for subreddit selection
  const handleSubredditSelect = async (option: any) => {
    const subreddit = option ? option.value : null;
    setSelectedSubreddit(subreddit);
    
    if (subreddit) {
      setIsLoadingTrending(true);
      try {
        await fetchRedditTrending(subreddit);
      } finally {
        setIsLoadingTrending(false);
      }
    }

    setRedditSearch(prev => ({
      ...prev,
      subreddit,
      query: prev.query,
      isValid: validateRedditSearch(prev.query)
    }));
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

  // Update handleGenerate to include Reddit search
  const handleGenerate = async () => {
    if (isRedditSearch) {
      if (!redditSearch.isValid) {
        setError('Please enter a valid search query');
        return;
      }
      setIsGenerating(true);
      try {
        const payload = {
          post_types: ["blog"],
          reddit_query: redditSearch.query,
          subreddit: selectedSubreddit  // Include optional subreddit
        };
        await api.post('/content/generate', payload);
        
        await new Promise(resolve => setTimeout(resolve, 3000));
        await fetchPosts({
          forceRefresh: true,
          timestamp: Date.now(),
          reset: true
        }, 0, 20);
        
        onClose();
      } catch (err: any) {
        console.error('Failed to generate blog:', err);
        if (err.response?.status === 403 && err.response?.data?.detail?.includes("Generation limit reached")) {
          toast.error('User has exceeded the generation limit');
        } else {
          setError('Failed to generate blog');
        }
      } finally {
        setIsGenerating(false);
      }
      return;
    }

    if (isCustomTopic) {
      if (!customTopic.isValid) {
        setError('Please enter a valid topic');
        return;
      }
      setIsGenerating(true);
      try {
        const payload = {
          post_types: ["blog"],
          topic: customTopic.topic
        };
        await api.post('/content/generate', payload);
        
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        await fetchPosts({
          forceRefresh: true,
          timestamp: Date.now(),
          reset: true
        }, 0, 20);
        
        onClose();
      } catch (err: any) {
        console.error('Failed to generate blog:', err);
        if (err.response?.status === 403 && err.response?.data?.detail?.includes("Generation limit reached")) {
          toast.error('User has exceeded the generation limit');
        } else {
          setError('Failed to generate blog');
        }
      } finally {
        setIsGenerating(false);
      }
      return;
    }

    if (isCustomUrl) {
      if (!customUrl.isValid) {
        setError('Please enter a valid URL');
        return;
      }
      setIsGenerating(true);
      try {
        const payload = {
          post_types: ["blog"],
          url: customUrl.url
        };
        await api.post('/content/generate', payload);
        
        // Increased wait time and added multiple refresh attempts
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // First refresh
        await fetchPosts({
          forceRefresh: true,
          timestamp: Date.now(),
          reset: true
        }, 0, 20);

        // // Second refresh after a short delay
        // setTimeout(async () => {
        //   await fetchPosts({
        //     forceRefresh: true,
        //     timestamp: Date.now(),
        //     reset: true
        //   }, 0, 20);
        // }, 2000);
        
        onClose();
      } catch (err: any) {
        console.error('Failed to generate blog:', err);
        if (
          err.response?.status === 403 &&
          err.response?.data?.detail?.includes("Generation limit reached")
        ) {
          toast.error('User has exceeded the generation limit');
        } else {
          setError('Failed to generate blog');
        }
      } finally {
        setIsGenerating(false);
      }
      return;
    }

    // For non-custom URL sources
    if (!selectedIdentifier) {
      setError('Please select a source');
      return;
    }

    const sourceData = sources.find(source => getUniqueId(source) === selectedIdentifier);
    if (!sourceData) {
      setError('Selected source not found');
      return;
    }

    setIsGenerating(true);
    
    try {
      const payload = {
        post_types: ["blog"],
        [selectedSource === 'twitter' 
          ? 'tweet_id' 
          : selectedSource === 'reddit'
            ? 'reddit_id'
            : 'url']: sourceData.source_identifier
      };
      
      await api.post('/content/generate', payload);
      
      // Increased wait time and added multiple refresh attempts
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // First refresh
      await fetchPosts({
        forceRefresh: true,
        timestamp: Date.now(),
        reset: true
      }, 0, 20);

      // Second refresh after a short delay
      setTimeout(async () => {
        await fetchPosts({
          forceRefresh: true,
          timestamp: Date.now(),
          reset: true
        }, 0, 20);
      }, 2000);
      
      onClose();
    } catch (err: any) {
      console.error('Failed to generate blog:', err);
      if (
        err.response?.status === 403 &&
        err.response?.data?.detail?.includes("Generation limit reached")
      ) {
        toast.error('User has exceeded the generation limit');
      } else {
        setError('Failed to generate blog');
      }
    } finally {
      setIsGenerating(false);
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
          className="cursor-pointer w-full overflow-hidden p-2" // Added flex-[0.8]
          onClick={() => setSelectedIdentifier(getUniqueId(source))}
        >
          <MicrolinkCard 
            url={source.source_identifier}
            contrast
            fetchdata
            lazy={{ threshold: 0.2 }}
            size="large" // Changed from large to small
            media={['image', 'logo']}
            className="!rounded-lg !border !border-gray-200 dark:!border-gray-700 pointer-events-none !max-w-full !transform !scale-90" // Added scale down
            style={{ objectFit: 'contain' }} // Removed flex: 0.8
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

  // Add topic input section
  const renderTopicInput = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <button
          onClick={() => {
            setSelectedSource(null);  // Reset selected source
            setIsCustomTopic(false);  // Reset custom topic mode
            setCustomTopic({ topic: '', isValid: false });  // Reset topic input
          }}
          className="flex items-center gap-2 text-sm text-blue-500 hover:text-blue-600"
        >
          <ChevronLeft className="h-4 w-4" />
          Back to sources
        </button>
      </div>
      <div className="p-6 border rounded-lg dark:border-gray-700">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Enter Topic or Research Query
        </label>
        <input
          type="text"
          value={customTopic.topic}
          onChange={handleTopicChange}
          placeholder="Enter your topic or research query..."
          className="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
        />
        {customTopic.topic && !customTopic.isValid && (
          <p className="mt-2 text-sm text-red-600">Topic must be at least 3 characters long</p>
        )}
        
        <div className="mt-6">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Trending Topics
          </h4>
          <div className="grid grid-cols-2 gap-2">
            {trendingTopics.map((topic) => (
              <button
                key={topic}
                onClick={() => setCustomTopic({ topic, isValid: true })}
                className="text-left px-3 py-2 text-sm rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                {topic}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  // Add Reddit search input section
  const getPaginatedTrendingTopics = useCallback((topics: any[]) => {
    const startIndex = (trendingPage - 1) * TRENDING_PER_PAGE;
    return topics.slice(startIndex, startIndex + TRENDING_PER_PAGE);
  }, [trendingPage]);

  const renderRedditSearch = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <button
          onClick={() => {
            setSelectedSource(null);
            setIsRedditSearch(false);
            setRedditSearch({ query: '', isValid: false, subreddit: null });
          }}
          className="flex items-center gap-2 text-sm text-blue-500 hover:text-blue-600"
        >
          <ChevronLeft className="h-4 w-4" />
          Back to sources
        </button>
      </div>

      <div className="border rounded-lg dark:border-gray-700">
        {/* Combined Search and Subreddit Selection */}
        <div className="p-6 border-b dark:border-gray-700">
          <div className="flex gap-4 items-start">
            {/* Topic Input */}
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Enter Topic for Reddit Search
              </label>
              <input
                type="text"
                value={redditSearch.query}
                onChange={handleRedditSearchChange}
                placeholder="Enter your topic..."
                className="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Subreddit Dropdown */}
            <div className="w-64">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Select Subreddit
              </label>
              <Select
                options={trendingRedditTopics.map(topic => ({ value: topic, label: `r/${topic}` }))}
                value={selectedSubreddit ? { value: selectedSubreddit, label: `r/${selectedSubreddit}` } : null}
                onChange={handleSubredditSelect}
                isClearable
                placeholder="Optional"
                className="react-select-container"
                classNamePrefix="react-select"
                menuPortalTarget={document.body}
                styles={{
                  menuPortal: (base) => ({
                    ...base,
                    zIndex: 9999
                  })
                }}
              />
            </div>
          </div>
        </div>

        {/* Trending Topics Section */}
        {selectedSubreddit && (
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Trending on r/{selectedSubreddit}
              </h4>
              {isLoadingTrending ? (
                <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
              ) : (
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setTrendingPage(page => Math.max(1, page - 1))}
                    disabled={trendingPage === 1}
                    className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded disabled:opacity-50"
                  >
                    ←
                  </button>
                  <span className="text-sm text-gray-500">
                    Page {trendingPage}
                  </span>
                  <button
                    onClick={() => setTrendingPage(page => page + 1)}
                    disabled={!redditTrendingTopics[selectedSubreddit] || 
                      getPaginatedTrendingTopics(redditTrendingTopics[selectedSubreddit]).length < TRENDING_PER_PAGE}
                    className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded disabled:opacity-50"
                  >
                    →
                  </button>
                </div>
              )}
            </div>
            
            {redditTrendingTopics[selectedSubreddit]?.length > 0 ? (
              <div className="grid grid-cols-2 gap-3">
                {getPaginatedTrendingTopics(redditTrendingTopics[selectedSubreddit]).map((topic) => (
                  <div
                    key={topic.url}
                    className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                    onClick={() => setRedditSearch({
                      query: topic.title,
                      isValid: true,
                      subreddit: selectedSubreddit
                    })}
                  >
                    <div className="flex flex-col h-full">
                      <h5 className="font-medium text-sm line-clamp-2 mb-2">{topic.title}</h5>
                      <div className="mt-auto flex items-center gap-3 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <MessageCircle className="w-3 h-3" />
                          {topic.num_comments}
                        </span>
                        <span className="flex items-center gap-1">
                          ⬆️ {topic.score}
                        </span>
                        <span className="flex items-center gap-1">
                          📊 {Math.round(topic.upvote_ratio * 100)}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : !isLoadingTrending && (
              <div className="text-center py-8 text-gray-500">
                No trending topics found
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );

  const renderSourceSelection = () => (
    <div className="grid grid-cols-2 gap-4">
      <button
        onClick={() => {
          setSelectedSource('twitter');
          setIsCustomUrl(false);
        }}
        className="group relative rounded-xl border border-gray-200 dark:border-gray-700 p-6 hover:border-blue-500 dark:hover:border-blue-500 transition-colors"
      >
        <div className="flex flex-col items-center gap-4">
          <Twitter className="h-8 w-8 text-blue-500" />
          <span className="text-sm font-medium">From Twitter</span>
        </div>
      </button>
      <button
        onClick={() => {
          setSelectedSource('web');
          setIsCustomUrl(false);
        }}
        className="group relative rounded-xl border border-gray-200 dark:border-gray-700 p-6 hover:border-green-500 dark:hover:border-green-500 transition-colors"
      >
        <div className="flex flex-col items-center gap-4">
          <Globe className="h-8 w-8 text-green-500" />
          <span className="text-sm font-medium">From Web</span>
        </div>
      </button>
      <button
        onClick={() => {
          setSelectedSource('topic');
          setIsCustomTopic(true);
        }}
        className="group relative rounded-xl border border-gray-200 dark:border-gray-700 p-6 hover:border-purple-500 dark:hover:border-purple-500 transition-colors"
      >
        <div className="flex flex-col items-center gap-4">
          <Search className="h-8 w-8 text-purple-500" />
          <span className="text-sm font-medium">From Topic</span>
        </div>
      </button>
      <button
        onClick={() => {
          setSelectedSource('reddit');
          setIsRedditSearch(true);
        }}
        className="group relative rounded-xl border border-gray-200 dark:border-gray-700 p-6 hover:border-orange-500 dark:hover:border-orange-500 transition-colors"
      >
        <div className="flex flex-col items-center gap-4">
          <MessageCircle className="h-8 w-8 text-orange-500" />
          <span className="text-sm font-medium">From Reddit</span>
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
              placeholder={getSearchPlaceholder()}
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
      <div className="px-4 py-2">
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
    // For Reddit search case
    if (isRedditSearch) {
      return !redditSearch.isValid || isGenerating;
    }
    
    // For topic case
    if (isCustomTopic) {
      return !customTopic.isValid || isGenerating;
    }
    
    // For custom URL case
    if (isCustomUrl) {
      return !customUrl.isValid || isGenerating;
    }
    
    // For regular sources
    return isGenerating || !selectedIdentifier;
  }, [isGenerating, selectedIdentifier, isCustomUrl, customUrl.isValid, isCustomTopic, customTopic.isValid, isRedditSearch, redditSearch.isValid]);

  const getGenerateButtonTooltip = useCallback((source?: SourceData) => {
    // For Reddit search case
    if (isRedditSearch) {
      if (!redditSearch.isValid) return 'Please enter a valid search query';
      if (isGenerating) return 'Generation in progress...';
      return 'Generate Blog';
    }
    
    // For topic case
    if (isCustomTopic) {
      if (!customTopic.isValid) return 'Please enter a valid topic';
      if (isGenerating) return 'Generation in progress...';
      return 'Generate Blog';
    }
    
    // For custom URL case
    if (isCustomUrl) {
      if (!customUrl.isValid) return 'Please enter a valid URL';
      if (isGenerating) return 'Generation in progress...';
      return 'Generate Blog';
    }
    
    // For regular sources
    if (isGenerating) return 'Generation in progress...';
    if (!selectedIdentifier) return 'Please select a source';
    return 'Generate Blog';
  }, [isGenerating, selectedIdentifier, isCustomUrl, customUrl.isValid, isCustomTopic, customTopic.isValid, isRedditSearch, redditSearch.isValid]);

  // Add getSearchPlaceholder function
  const getSearchPlaceholder = () => {
    switch(selectedSource) {
      case 'twitter':
        return 'Search tweets...';
      case 'reddit':
        return 'Search Reddit posts...';
      default:
        return 'Search URLs...';
    }
  };

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      {/* Dark overlay */}
      <div className="fixed inset-0 bg-black/30 backdrop-blur-sm" aria-hidden="true" />

      {/* Update container z-index */}
      <div className="fixed inset-0 overflow-y-auto z-[50]">
        <div className="flex min-h-full items-center justify-center p-4">
          <Dialog.Panel className="w-full max-w-4xl rounded-xl bg-white dark:bg-gray-800 shadow-xl transition-all">
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

            {/* Modal content - Remove fixed height constraints */}
            <div className="px-6 py-4">
              {error && (
                <div className="mb-4 p-4 bg-red-50 text-red-600 rounded-lg">
                  {error}
                </div>
              )}

              {/* Remove max-height constraint */}
              <div>
                {!selectedSource && renderSourceSelection()}
                {selectedSource === 'topic' && renderTopicInput()}
                {selectedSource === 'reddit' && renderRedditSearch()}
                {selectedSource === 'web' && !isCustomUrl && renderSourceContentSection()}
                {selectedSource === 'twitter' && !isCustomUrl && renderSourceContentSection()}
                {selectedSource === 'web' && isCustomUrl && renderCustomUrlInput()}
              </div>
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
                    disabled={isRedditSearch
                      ? !redditSearch.isValid || isGenerating
                      : isCustomTopic 
                        ? !customTopic.isValid || isGenerating
                        : isCustomUrl 
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
