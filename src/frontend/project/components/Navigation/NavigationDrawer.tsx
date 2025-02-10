import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import { useEditorStore } from '../../store/editorStore';
import { Post } from '../../types';
import { Loader, Search, Filter, X, RefreshCw } from 'lucide-react';
import debounce from 'lodash.debounce';

interface NavigationDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

interface FilterState {
  post_type: string;
  status: string;
  domain: string;
  tag_name: string;
  created_after: string;
  created_before: string;
}

const QUICK_FILTERS = [
  { label: 'All', value: '' },
  { label: 'Published', value: 'Published' },
  { label: 'Drafts', value: 'Draft' },
  { label: 'Recent', value: 'recent' }
];

export const NavigationDrawer: React.FC<NavigationDrawerProps> = ({ isOpen, onClose }) => {
  const { 
    posts, 
    currentPost, 
    setCurrentPost, 
    fetchPosts, 
    limit, 
    isLoading,
    hasReachedEnd,
  } = useEditorStore();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<FilterState>({
    post_type: '',
    status: '',
    domain: '',
    tag_name: '',
    created_after: '',
    created_before: ''
  });
  const [selectedQuickFilter, setSelectedQuickFilter] = useState('');
  const [isResetting, setIsResetting] = useState(false);

  // Move filteredPosts before its usage
  const filteredPosts = useMemo(() => {
    if (!posts || posts.length === 0 || (isLoading && !searchTerm && !selectedQuickFilter)) return [];
    
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
      })
      .sort((a, b) => new Date(b.updatedAt || 0).getTime() - new Date(a.updatedAt || 0).getTime());
  }, [posts, searchTerm, selectedQuickFilter, isLoading]);

  // Add latestDate calculation for post indicators
  const latestDate = useMemo(() => {
    if (!filteredPosts.length) return null;
    return new Date(filteredPosts[0].updatedAt);
  }, [filteredPosts]);

  const loadMoreRef = useRef<HTMLDivElement | null>(null);
  const initialFetchDoneRef = useRef(false);
  const isFetchingRef = useRef(false);

  // Replace the debounced handleLoadMore with a useCallback version:
  const handleLoadMore = useCallback(async () => {
    // Return if already fetching/loading or reached end
    if (isFetchingRef.current || hasReachedEnd || isLoading) return;
    
    isFetchingRef.current = true;
    const previousScrollTop = loadMoreRef.current?.scrollTop || 0;
    
    try {
      const newPosts = await fetchPosts({ timestamp: Date.now() }, posts.length, limit);
      useEditorStore.setState(state => ({
        ...state,
        posts: [...state.posts, ...(Array.isArray(newPosts) ? newPosts : [])]
      }));
      if (loadMoreRef.current) {
        loadMoreRef.current.scrollTop = previousScrollTop;
      }
    } catch (error) {
      console.error('Error loading more posts:', error);
    } finally {
      isFetchingRef.current = false;
    }
  }, [fetchPosts, posts.length, hasReachedEnd, limit, isLoading]);

  // Replace the existing scroll listener effect with a debounced version similar to the sample:
  useEffect(() => {
    const scrollContainer = loadMoreRef.current;
    if (!scrollContainer) return;
    
    const handleScroll = debounce(() => {
      const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
      if (scrollHeight - (scrollTop + clientHeight) < 100 && !isLoading && !hasReachedEnd) {
        handleLoadMore();
      }
    }, 200, { leading: true, trailing: true });
    
    scrollContainer.addEventListener('scroll', handleScroll);
    return () => {
      scrollContainer.removeEventListener('scroll', handleScroll);
      handleScroll.cancel();
    };
  }, [handleLoadMore, isLoading, hasReachedEnd, posts.length, limit]);

  useEffect(() => {
    if (!initialFetchDoneRef.current && !isLoading) {
      initialFetchDoneRef.current = true;
      fetchPosts({
        timestamp: Date.now(),
        forceRefresh: true
      }, 0, limit);
    }
  }, [fetchPosts, isLoading, limit]);

  // Client-side search handler
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    
    // Reset filters and quick filters when searching
    if (!showFilters) {
      setFilters({
        post_type: '',
        status: '',
        domain: '',
        tag_name: '',
        created_after: '',
        created_before: ''
      });
      setSelectedQuickFilter('');
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
        created_after: '',
        created_before: ''
      });
      setSelectedQuickFilter('');
      setShowFilters(false);
      
      // Clear the posts in the store
      useEditorStore.setState(state => ({
        ...state,
        posts: [],
        hasReachedEnd: false
      }));

      // Reset ref to allow fresh fetch
      initialFetchDoneRef.current = false;
      isFetchingRef.current = false;

      // Force fresh fetch with clean state
      await fetchPosts({
        timestamp: Date.now(),
        forceRefresh: true,
        noCache: true
      }, 0, limit);

    } catch (error) {
      console.error('Error resetting posts:', error);
    } finally {
      setIsResetting(false);
    }
  };

  // API-based filter application
  const handleApplyFilters = async () => {
    setIsResetting(true);
    
    try {
      const cleanedFilters = Object.entries(filters).reduce((acc, [key, value]) => {
        if (value && value !== 'All') {
          acc[key] = value;
        }
        return acc;
      }, {} as Record<string, any>);

      await fetchPosts({
        ...cleanedFilters,
        timestamp: Date.now(),
        forceRefresh: true,
        noCache: true
      }, 0, limit);

      setShowFilters(false);
    } catch (error) {
      console.error('Error applying filters:', error);
    } finally {
      setIsResetting(false);
    }
  };

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleQuickFilterClick = (value: string) => {
    // Toggle filter if clicking the same one
    const newValue = value === selectedQuickFilter ? '' : value;
    setSelectedQuickFilter(newValue);

    // Reset other filters when using quick filters
    setFilters({
      post_type: '',
      status: '',
      domain: '',
      tag_name: '',
      created_after: '',
      created_before: ''
    });
    setSearchTerm('');
  };

  const handlePostSelect = (post: Post) => {
    setCurrentPost(post);
    onClose();
  };

  // Reset filters when drawer is closed
  useEffect(() => {
    if (!isOpen) {
      // Reset the filter panel state
      setShowFilters(false);
      
      // Only reset filters if they're not actively being used
      if (!searchTerm && !selectedQuickFilter && !Object.values(filters).some(val => val)) {
        handleReset();
      }
    }
  }, [isOpen]);

  return (
    <div
      className={`fixed inset-y-0 left-16 w-80 bg-white dark:bg-gray-800 shadow-xl transform transition-transform duration-300 ease-in-out z-40 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      } border-r dark:border-gray-700`}
    >
      <div className="h-full flex flex-col">
        {/* Quick Filter Chips */}
        <div className="p-4 border-b dark:border-gray-700">
          <div className="flex flex-wrap gap-2 mb-4">
            {QUICK_FILTERS.map(filter => (
              <button
                key={filter.value}
                onClick={() => handleQuickFilterClick(filter.value)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                  selectedQuickFilter === filter.value
                    ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                    : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {filter.label}
              </button>
            ))}
          </div>

          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search posts..."
              value={searchTerm}
              onChange={handleSearchChange}
              className="w-full pl-9 pr-12 py-2 bg-gray-50 dark:bg-gray-700 rounded-lg border-0 focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-full transition-colors"
            >
              <Filter className={`w-4 h-4 ${showFilters ? 'text-blue-500' : 'text-gray-400'}`} />
            </button>
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
                      name="created_after"
                      value={filters.created_after}
                      onChange={handleFilterChange}
                      className="w-full p-2 rounded-lg bg-gray-50 dark:bg-gray-700 border-0"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">To</label>
                    <input
                      type="date"
                      name="created_before"
                      value={filters.created_before}
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

        <div ref={loadMoreRef} className="flex-1 overflow-auto max-h-[calc(100vh-120px)] relative">
          <div className="min-h-full">
            {(isLoading || isResetting) && (
              <div className="absolute inset-0 bg-white/50 dark:bg-gray-800/50 flex items-center justify-center z-50">
                <Loader className="w-6 h-6 animate-spin text-blue-500" />
              </div>
            )}
            
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
                      className="w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700"
                    >
                      <h3 className={`mb-1 truncate ${
                        latestDate && new Date(post.updatedAt).getDate() === latestDate.getDate() 
                          ? 'font-medium' 
                          : 'font-normal'
                      }`}>
                        {post.title}
                      </h3>
                      <div className="flex justify-between items-center">
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {new Date(post.updatedAt).toLocaleDateString()}
                        </p>
                        <span className={`inline-block px-2 py-1 text-xs font-semibold rounded ${
                          post.status === 'Published'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : post.status === 'Rejected'
                            ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                            : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                        }`}>
                          {post.status}
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
                {isLoading || isResetting ? '' : 'No posts found'}
              </div>
            )}
            
            {/* Load more indicator */}
            <div className="h-10 flex justify-center items-center">
              {(isLoading || isResetting) && filteredPosts.length > 0 && (
                <Loader className="w-4 h-4 animate-spin text-blue-500" />
              )}
              {hasReachedEnd && posts.length > 0 && (
                <span className="text-sm text-gray-500">No more posts</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};