import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import { useEditorStore } from '../../store/editorStore';
import { Loader, Search, Filter, X, RefreshCw, Trash2, Zap } from 'lucide-react';
import debounce from 'lodash.debounce';
import { Post } from '../../types/editor';
import toast from 'react-hot-toast';
import { cacheManager } from '../../services/cacheManager';
import Tippy from '@tippyjs/react';
import api from '../../services/api'; // Import API to handle post deletion

interface NavigationDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigateToEditor?: () => void; // New prop for navigation handling
}

interface FilterState {
  post_type: string;
  status: string;
  domain: string;
  tag_name: string;
  updated_after: string;
  updated_before: string;
}

const QUICK_FILTERS = [
  { label: 'All', value: '' },
  { label: 'Published', value: 'Published' },
  { label: 'Drafts', value: 'Draft' },
];

// Store cache keys for different filters
const FILTER_CACHE_KEYS = {
  ALL: 'all_posts',
  PUBLISHED: 'published_posts',
  DRAFTS: 'draft_posts'
};

export const NavigationDrawer: React.FC<NavigationDrawerProps> = ({ 
  isOpen, 
  onClose,
  onNavigateToEditor 
}) => {
  const { 
    posts, 
    currentPost, 
    setCurrentPost, 
    fetchPosts, 
    limit, 
    isLoading,
    hasReachedEnd,
    // Remove deletePost from here since it doesn't exist in the store
    isContentUpdated,
    runningGenerations, // Add the runningGenerations from the store
    hasRunningGenerations // Add this flag from the store
  } = useEditorStore();
  
  const isListLoading = useEditorStore(state => state.isListLoading);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<FilterState>({
    post_type: '',
    status: '',
    domain: '',
    tag_name: '',
    updated_after: '',
    updated_before: ''
  });
  const [selectedQuickFilter, setSelectedQuickFilter] = useState('');
  const [isResetting, setIsResetting] = useState(false);
  const [isServerFiltered, setIsServerFiltered] = useState(false);
  const [activeFilterCount, setActiveFilterCount] = useState(0);

  // Track if initial fetch has been done
  const initialFetchDoneRef = useRef(false);
  const isFetchingRef = useRef(false);
  const drawerOpenedRef = useRef(false);
  const lastFetchRef = useRef(0);
  const fetchCounterRef = useRef(0); // Counter to track fetch attempts

  // Track last loaded position for each filter type
  const filterScrollPositionsRef = useRef<Record<string, number>>({});
  // Track loaded posts count for each filter
  const filterPostsCountRef = useRef<Record<string, number>>({});
  // Track if filter has reached end
  const filterReachedEndRef = useRef<Record<string, boolean>>({});

  // Get current filter cache key
  const getCurrentFilterKey = useCallback(() => {
    if (selectedQuickFilter === 'Published') return FILTER_CACHE_KEYS.PUBLISHED;
    if (selectedQuickFilter === 'Draft') return FILTER_CACHE_KEYS.DRAFTS;
    return FILTER_CACHE_KEYS.ALL;
  }, [selectedQuickFilter]);

  // Filter posts client-side when possible
  const filteredPosts = useMemo(() => {
    if (!posts || posts.length === 0) return [];
    
    // If server-side filters are active, don't filter client-side
    if (isServerFiltered) {
      return posts;
    }
    
    // Only filter if we have search term or quick filter
    if (!searchTerm && !selectedQuickFilter) {
      return posts;
    }
    
    return posts
      .filter((post) => {
        if (!post) return false;
        
        // Client-side title search
        const titleMatch = searchTerm 
          ? post.title?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false
          : true;

        // Quick filter handling
        if (selectedQuickFilter) {
          if (selectedQuickFilter === 'recent') {
            const isRecent = Date.now() - new Date(post.createdAt).getTime() <= 7 * 24 * 60 * 60 * 1000;
            if (!isRecent) return false;
          } else if (post.status !== selectedQuickFilter) {
            return false;
          }
        }

        return titleMatch;
      });
  }, [posts, searchTerm, selectedQuickFilter, isServerFiltered]);

  // Add latestDate calculation for post indicators
  const latestDate = useMemo(() => {
    if (!filteredPosts.length) return null;
    return new Date(filteredPosts[0].updatedAt);
  }, [filteredPosts]);

  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  // Improved logic to check if we need to fetch data
  const shouldFetchData = useCallback(() => {
    // 1. If content has been updated (new blog generated)
    if (isContentUpdated) {
      console.log('Fetching due to content update');
      return true;
    }
    
    // 2. If there's no data yet
    if (posts.length === 0) {
      console.log('Fetching because posts are empty');
      return true;
    }
    
    // 3. Check if we have a valid cache entry for empty filters (default list)
    const defaultCacheKey = JSON.stringify({ filters: {}, skip: 0, limit });
    const cachedData = cacheManager.getContentFromCache(defaultCacheKey);
    
    if (!cachedData) {
      console.log('Fetching because no cached data found');
      return true;
    }
    
    console.log('Using cached data, not fetching');
    return false;
  }, [posts.length, isContentUpdated, limit]);

  // Optimize the handleLoadMore callback - simplified version
  const handleLoadMore = useCallback(async () => {
    if (isFetchingRef.current || hasReachedEnd || isLoading) {
      return;
    }
    
    console.log('Executing load more: posts.length =', posts.length);
    isFetchingRef.current = true;
    
    try {
      // Create appropriate filters based on quick filter selection
      const filterParams: Record<string, any> = { timestamp: Date.now() };
      if (selectedQuickFilter) {
        filterParams.status = selectedQuickFilter;
      }
      
      // Fetch more posts with current filter
      await fetchPosts(filterParams, posts.length, limit);
    } catch (error) {
      console.error('Error loading more posts:', error);
    } finally {
      isFetchingRef.current = false;
    }
  }, [fetchPosts, posts.length, hasReachedEnd, limit, isLoading, selectedQuickFilter]);

  // Optimize scroll listener with proper cleanup and debounce
  useEffect(() => {
    const scrollContainer = loadMoreRef.current;
    if (!scrollContainer) return;
    
    const handleScroll = debounce(() => {
      if (!scrollContainer) return;
      
      const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
      
      // Only log in development
      if (process.env.NODE_ENV === 'development') {
        console.log('Scroll metrics:', {
          distanceToBottom: scrollHeight - (scrollTop + clientHeight),
          isLoading,
          hasReachedEnd,
          postsLength: posts.length
        });
      }
      
      const distanceToBottom = scrollHeight - (scrollTop + clientHeight);
      const threshold = 100; // Smaller threshold for more reliable triggering
      
      if (distanceToBottom < threshold && !isLoading && !isFetchingRef.current && !hasReachedEnd && posts.length > 0) {
        handleLoadMore();
      }
    }, 100);
    
    scrollContainer.addEventListener('scroll', handleScroll);
    
    return () => {
      scrollContainer.removeEventListener('scroll', handleScroll);
      handleScroll.cancel();
    };
  }, [handleLoadMore, isLoading, hasReachedEnd, posts.length]);

  // Enhanced data fetching logic for when drawer opens
  useEffect(() => {
    if (isOpen && !isListLoading && !isFetchingRef.current) {
      const justOpened = !drawerOpenedRef.current;
      drawerOpenedRef.current = true;
      
      const currentFilterKey = getCurrentFilterKey();
      
      // Check if we have content for this filter already
      if (posts.length > 0 && filterPostsCountRef.current[currentFilterKey]) {
        // We already have data for this filter, restore scroll position
        requestAnimationFrame(() => {
          if (loadMoreRef.current) {
            const savedPos = filterScrollPositionsRef.current[currentFilterKey] || 0;
            loadMoreRef.current.scrollTop = savedPos;
          }
        });
        return;
      }
      
      // Check if we should fetch fresh data
      if ((justOpened && shouldFetchData()) || !initialFetchDoneRef.current) {
        console.log('Fetching posts on drawer open for filter:', currentFilterKey);
        
        // Mark initial fetch done
        initialFetchDoneRef.current = true;
        
        // Prepare filter params based on current filter
        const filterParams: Record<string, any> = { timestamp: Date.now() };
        if (selectedQuickFilter) {
          filterParams.status = selectedQuickFilter;
        }
        
        // Fetch data for current filter
        fetchPosts(filterParams, 0, limit).then(() => {
          // Update the filter's post count after fetch
          filterPostsCountRef.current[currentFilterKey] = posts.length;
        });
      }
    }
    
    // Reset the drawer opened state when it closes
    if (!isOpen) {
      drawerOpenedRef.current = false;
    }
  }, [isOpen, fetchPosts, isListLoading, limit, shouldFetchData, posts.length, getCurrentFilterKey, selectedQuickFilter]);

  // Debounced search that uses client-side filtering when possible
  const debouncedSearch = useMemo(() => {
    return debounce((term: string) => {
      setSearchTerm(term);
      // If search term is long enough, we need to filter server-side
      if (term.length > 3) {
        fetchPosts({
          title_contains: term,
          timestamp: Date.now()
        }, 0, limit);
      }
    }, 500);
  }, [fetchPosts, limit]);

  // Clean up the debounce on unmount
  useEffect(() => {
    return () => {
      debouncedSearch.cancel();
    };
  }, [debouncedSearch]);

  // Client-side search handler
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Immediately update UI with the new value
    setSearchTerm(value);
    
    // Reset server-side filters when searching
    if (isServerFiltered) {
      setIsServerFiltered(false);
      setActiveFilterCount(0);
    }
    
    // Reset filters and quick filters when searching
    if (!showFilters) {
      setFilters({
        post_type: '',
        status: '',
        domain: '',
        tag_name: '',
        updated_after: '',
        updated_before: ''
      });
      setSelectedQuickFilter('');
    }
    
    // Debounce the actual search operation
    debouncedSearch(value);
  };

  // Force refresh data manually
  const handleManualRefresh = async () => {
    setIsResetting(true);
    
    try {
      // Update last fetch time and reset fetch counter
      lastFetchRef.current = Date.now();
      fetchCounterRef.current = 0;
      
      // Force fetch with clean state
      await fetchPosts({
        timestamp: Date.now(),
        forceRefresh: true
      }, 0, limit);
      
      toast.success('Posts refreshed successfully');
    } catch (error) {
      console.error('Error refreshing posts:', error);
      toast.error('Failed to refresh posts');
    } finally {
      setIsResetting(false);
    }
  };

  // API-based reset handler
  const handleReset = async () => {
    setIsResetting(true);
    
    try {
      // Reset local state
      setSearchTerm('');
      setFilters({
        post_type: '',
        status: '',
        domain: '',
        tag_name: '',
        updated_after: '',
        updated_before: ''
      });
      setSelectedQuickFilter('');
      setShowFilters(false);
      setIsServerFiltered(false);
      setActiveFilterCount(0);
      
      // Reset filter-specific tracking
      filterScrollPositionsRef.current = {};
      filterPostsCountRef.current = {};
      filterReachedEndRef.current = {};
      
      // Clear the posts in the store
      useEditorStore.setState(state => ({
        ...state,
        posts: [],
        hasReachedEnd: false
      }));

      // Reset ref to allow fresh fetch
      initialFetchDoneRef.current = false;
      isFetchingRef.current = false;
      lastFetchRef.current = Date.now();
      fetchCounterRef.current = 0;

      // Force fresh fetch with clean state
      await fetchPosts({
        timestamp: Date.now(),
        forceRefresh: true
      }, 0, limit);
    } catch (error) {
      console.error('Error resetting posts:', error);
      toast.error('Failed to reset posts');
    } finally {
      setIsResetting(false);
    }
  };

  const handleApplyFilters = async () => {
    setIsResetting(true);
    
    try {
      // Clean and structure filters for API
      const apiFilters = Object.entries(filters).reduce((acc, [key, value]) => {
        if (value && value !== 'All') {
          // Handle date filters specially to ensure proper ISO format
          if (key === 'updated_after' || key === 'updated_before') {
            acc[key] = new Date(value).toISOString();
          } else {
            acc[key] = value;
          }
        }
        return acc;
      }, {} as Record<string, any>);

      // Count active filters for UI indicator
      const filterCount = Object.keys(apiFilters).length;
      setActiveFilterCount(filterCount);
      
      // Set server filtered flag if we have any filters
      setIsServerFiltered(filterCount > 0);

      // Update last fetch time
      lastFetchRef.current = Date.now();

      // Clear search term and quick filters when applying advanced filters
      setSearchTerm('');
      setSelectedQuickFilter('');

      // Ensure filters are properly structured for the API
      const fetchFilters = {
        ...apiFilters,
        timestamp: Date.now()
      };

      console.log('Applying filters:', fetchFilters);
      await fetchPosts(fetchFilters, 0, limit);

      setShowFilters(false);
    } catch (error) {
      console.error('Error applying filters:', error);
      toast.error('Failed to apply filters');
    } finally {
      setIsResetting(false);
    }
  };

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  // Simplified quick filter click handler
  const handleQuickFilterClick = (value: string) => {
    // Toggle filter if clicking the same one
    const newValue = value === selectedQuickFilter ? '' : value;
    
    // Always clear existing state before applying new filter
    setSearchTerm('');
    setSelectedQuickFilter(newValue);
    
    // Reset server-side filters when using quick filters
    setIsServerFiltered(false);
    setActiveFilterCount(0);
    
    // Reset other filters
    setFilters({
      post_type: '',
      status: '',
      domain: '',
      tag_name: '',
      updated_after: '',
      updated_before: ''
    });
    
    // Clear the posts in the store to prevent filter confusion
    useEditorStore.setState(state => ({
      ...state,
      posts: [],
      hasReachedEnd: false
    }));
    
    // Set loading state to true to show loading indicator
    useEditorStore.setState(state => ({ ...state, isListLoading: true }));
    
    // Always fetch fresh data for the new filter
    const apiFilters = newValue ? { status: newValue } : {};
    
    // Short delay to allow UI to update before fetch
    setTimeout(() => {
      fetchPosts({
        ...apiFilters,
        timestamp: Date.now(),
        forceRefresh: true // Always force refresh for reliable filter switching
      }, 0, limit);
    }, 50);
  };

  const handlePostSelect = (post: Post) => {
    setCurrentPost(post);
    // Navigate to editor if provided
    if (onNavigateToEditor) {
      onNavigateToEditor();
    }
    onClose();
  };

  const handleDelete = async (e: React.MouseEvent, threadId: string) => {
    e.stopPropagation(); // Prevent post selection when clicking delete
    if (window.confirm('Are you sure you want to delete this post?')) {
      try {
        // Use the api.deleteContent method instead of non-existent deletePost
        await api.delete(`/content/thread/${threadId}`);
        toast.success('Post deleted successfully');
        
        // Refresh the posts list after deletion
        fetchPosts({
          timestamp: Date.now(),
          forceRefresh: true
        }, 0, limit);
      } catch (error) {
        toast.error('Failed to delete post');
      }
    }
  };

  // Get active generation thread IDs for highlighting
  const generatingThreadIds = useMemo(() => {
    return Object.entries(runningGenerations)
      .filter(([_, gen]) => gen.status === 'initializing' || gen.status === 'running')
      .map(([id]) => id);
  }, [runningGenerations]);

  // Don't reset filters when drawer is closed to maintain state between openings
  return (
    <>
      {/* Add backdrop overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 dark:bg-black/40 z-30 cursor-pointer"
          onClick={onClose}
          aria-hidden="true"
        />
      )}
      <div
        className={`fixed inset-y-0 left-16 w-80 bg-white dark:bg-gray-800 shadow-xl transform transition-transform duration-300 ease-in-out z-40 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } border-r dark:border-gray-700`}
      >
        <div className="h-full flex flex-col pt-10">
          {/* Quick Filter Chips */}
          <div className="px-4 pb-4 border-b dark:border-gray-700">
            <div className="flex items-center gap-2 mb-6 px-1">
              {QUICK_FILTERS.map(filter => (
                <button
                  key={filter.value}
                  onClick={() => handleQuickFilterClick(filter.value)}
                  className={`flex-1 min-w-0 px-3 py-2 rounded-full text-sm font-medium transition-colors ${
                    selectedQuickFilter === filter.value
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  <span className="block truncate">{filter.label}</span>
                </button>
              ))}
            </div>

            <div className="relative px-1">
              <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search posts..."
                value={searchTerm}
                onChange={handleSearchChange}
                className="w-full pl-9 pr-12 py-2 bg-gray-50 dark:bg-gray-700 rounded-lg border-0 focus:ring-2 focus:ring-blue-500"
              />
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center gap-2">
                {isServerFiltered && (
                  <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-blue-500 rounded-full">
                    {activeFilterCount}
                  </span>
                )}
                {/* Add manual refresh button */}
                <button
                  onClick={handleManualRefresh}
                  disabled={isListLoading || isResetting}
                  className="p-1 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-full transition-colors"
                  title="Refresh posts"
                >
                  <RefreshCw className={`w-4 h-4 text-gray-400 ${isListLoading || isResetting ? 'animate-spin text-blue-500' : ''}`} />
                </button>
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className="p-1 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-full transition-colors"
                >
                  <Filter className={`w-4 h-4 ${showFilters || isServerFiltered ? 'text-blue-500' : 'text-gray-400'}`} />
                </button>
              </div>
            </div>

            {/* Filter Panel Overlay */}
            {showFilters && (
              <div className="absolute z-10 left-4 right-4 mt-2 p-4 bg-white dark:bg-gray-800 rounded-xl shadow-lg border dark:border-gray-700">
                {isResetting && (
                  <div className="absolute inset-0 bg-white/50 dark:bg-gray-800/50 flex items-center justify-center z-50 rounded-xl">
                    <Loader className="w-6 h-6 animate-spin text-blue-500" />
                  </div>
                )}
                
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="font-medium">Filters</h3>
                    <button
                      onClick={() => setShowFilters(false)}
                      className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Status</label>
                    <select
                      name="status"
                      value={filters.status}
                      onChange={handleFilterChange}
                      className="w-full p-2 rounded-lg bg-gray-50 dark:bg-gray-700 border-0"
                    >
                      <option value="">All Status</option>
                      <option value="Draft">Draft</option>
                      <option value="Published">Published</option>
                      <option value="Scheduled">Scheduled</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Tag</label>
                    <input
                      type="text"
                      name="tag_name"
                      value={filters.tag_name}
                      onChange={handleFilterChange}
                      placeholder="Filter by tag..."
                      className="w-full p-2 rounded-lg bg-gray-50 dark:bg-gray-700 border-0"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-sm font-medium mb-1">From</label>
                      <input
                        type="date"
                        name="updated_after"
                        value={filters.updated_after}
                        onChange={handleFilterChange}
                        className="w-full p-2 rounded-lg bg-gray-50 dark:bg-gray-700 border-0"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">To</label>
                      <input
                        type="date"
                        name="updated_before"
                        value={filters.updated_before}
                        onChange={handleFilterChange}
                        className="w-full p-2 rounded-lg bg-gray-50 dark:bg-gray-700 border-0"
                      />
                    </div>
                  </div>

                  <div className="flex gap-2 pt-2">
                    <button
                      onClick={handleReset}
                      disabled={isResetting || isLoading}
                      className="flex-1 px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 text-sm flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                      {isResetting ? (
                        <>
                          <RefreshCw className="w-4 h-4 animate-spin" />
                          Resetting...
                        </>
                      ) : (
                        'Reset'
                      )}
                    </button>
                    <button
                      onClick={handleApplyFilters}
                      disabled={isResetting || isLoading}
                      className="flex-1 px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                      {isResetting ? (
                        <>
                          <Loader className="w-4 h-4 animate-spin" />
                          Applying...
                        </>
                      ) : (
                        'Apply Filters'
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Active generations indicator */}
          {hasRunningGenerations && (
            <div className="px-4 py-2 bg-blue-50 dark:bg-blue-900/20 border-b dark:border-gray-700 flex items-center">
              <Zap className="w-4 h-4 text-blue-500 mr-2 animate-pulse" />
              <span className="text-sm text-blue-700 dark:text-blue-300">
                Content generation in progress
              </span>
            </div>
          )}

          <div ref={loadMoreRef} className="flex-1 overflow-auto max-h-[calc(100vh-120px)] relative scrollbar-hide">
            {isListLoading && (
              <div className="absolute inset-0 bg-white/50 dark:bg-gray-800/50 flex items-center justify-center z-50">
                <Loader className="w-6 h-6 animate-spin text-blue-500" />
              </div>
            )}
            
            {/* Server filter indicator */}
            {isServerFiltered && (
              <div className="px-4 py-2 bg-blue-50 dark:bg-blue-900/30 border-b dark:border-gray-700 flex justify-between items-center">
                <span className="text-sm text-blue-700 dark:text-blue-300">
                  {activeFilterCount} {activeFilterCount === 1 ? 'filter' : 'filters'} applied
                </span>
                <button
                  onClick={async () => {
                    setIsResetting(true);
                    try {
                      await handleReset();
                    } finally {
                      setIsResetting(false);
                    }
                  }}
                  disabled={isResetting}
                  className="text-xs text-blue-600 dark:text-blue-400 hover:underline disabled:opacity-50"
                >
                  {isResetting ? 'Clearing...' : 'Clear'}
                </button>
              </div>
            )}
            
            <div className="min-h-full">
              {filteredPosts.length > 0 ? (
                <div className="relative">
                  {filteredPosts.map((post) => (
                    <div 
                      key={post.id}
                      className={`relative border-b dark:border-gray-700 ${
                        currentPost?.id === post.id ? 'bg-gray-100 dark:bg-gray-700' : ''
                      }`}
                    >
                      <button
                        onClick={() => handlePostSelect(post)}
                        className="w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700 group"
                      >
                        <div className="flex justify-between items-start">
                          <h3 className={`mb-1 break-words leading-snug line-clamp-2 flex-1 ${
                            latestDate && new Date(post.updatedAt).getDate() === latestDate.getDate() 
                              ? 'font-medium' 
                              : 'font-normal'
                          }`}>
                            {/* Show generation indicator if thread_id is in active generations */}
                            {generatingThreadIds.includes(post.thread_id) && (
                              <Tippy content="Content being generated">
                                <span className="inline-flex items-center mr-2">
                                  <Zap className="w-3.5 h-3.5 text-blue-500 animate-pulse" />
                                </span>
                              </Tippy>
                            )}
                            {post.title}
                          </h3>
                          <button
                            onClick={(e) => handleDelete(e, post.thread_id)}
                            className="p-1.5 opacity-0 group-hover:opacity-100 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-full transition-opacity ml-2 -mr-1"
                            title="Delete post"
                          >
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </button>
                        </div>
                        <div className="flex justify-between items-center">
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {new Date(post.updatedAt).toLocaleDateString()}
                          </p>
                          <span className={`inline-block px-2 py-1 text-xs font-semibold rounded ${
                            generatingThreadIds.includes(post.thread_id)
                              ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                              : post.status === 'Published'
                              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                              : post.status === 'Rejected'
                              ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                              : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                          }`}>
                            {generatingThreadIds.includes(post.thread_id) ? 'Generating' : post.status}
                          </span>
                        </div>
                      </button>
                      {latestDate && new Date(post.updatedAt).getDate() === latestDate.getDate() && (
                        <div className="absolute top-1 right-1">
                          <span className="inline-block w-2 h-2 bg-green-500 rounded-full"></span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-4 text-center text-gray-500">
                  {isListLoading ? 'Loading...' : 'No posts found'}
                </div>
              )}
              
              {/* Load more indicator - simplified */}
              {!isListLoading && !hasReachedEnd && posts.length > 0 && (
                <div className="h-10 flex justify-center items-center" onClick={handleLoadMore}>
                  <button className="text-sm text-blue-500 flex items-center gap-1">
                    <Loader className="w-4 h-4 animate-spin text-blue-500" />
                    Loading more...
                  </button>
                </div>
              )}
              {hasReachedEnd && posts.length > 0 && (
                <div className="h-10 flex justify-center items-center">
                  <span className="text-sm text-gray-500">No more posts</span>
                </div>
              )}
              
              {/* Use a scroll-to-bottom helper button when less than 10 items to help trigger pagination */}
              {!isListLoading && !hasReachedEnd && 
                posts.length > 0 && posts.length < 10 && (
                <div className="h-12 flex justify-center items-center">
                  <button 
                    onClick={handleLoadMore}
                    className="text-sm text-blue-500 flex items-center gap-1 px-3 py-1 border border-blue-200 rounded-full hover:bg-blue-50 dark:hover:bg-blue-900/30"
                  >
                    Load more posts
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};