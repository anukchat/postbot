import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import {
  Search,
  Plus,
  Moon,
  Sun,
  Filter,
  ChevronRight,
  ChevronLeft,
  AlertCircle,
  Loader // Add the Loader icon
} from 'lucide-react';
import { useEditorStore } from '../../store/editorStore';
import { EditorToolbar } from '../Sidebar/EditorToolbar';
import debounce from 'lodash.debounce'; // Add this import
import { Post } from '../../types';

interface SidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

interface FilterState {
  title_contains: string;
  post_type: string;
  status: string;
  domain: string;
  tag_name: string;
  source_type: string;
  created_after: string;
  created_before: string;
  updated_after: string;
  updated_before: string;
  media_type: string;
  url_type: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ isCollapsed, onToggleCollapse }) => {
  const { 
    posts, 
    currentPost, 
    setCurrentPost, 
    isDarkMode, 
    toggleTheme, 
    fetchPosts, 
    fetchMorePosts, 
    skip, 
    limit, 
    totalPosts, 
    isLoading,
    hasReachedEnd 
  } = useEditorStore();
  const [searchTerm, setSearchTerm] = React.useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<FilterState>({
    title_contains: '',
    post_type: '',
    status: 'All',
    domain: '',
    tag_name: '',
    source_type: '',
    created_after: '',
    created_before: '',
    updated_after: '',
    updated_before: '',
    media_type: '',
    url_type: ''
  });
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  const handleLoadMore = useCallback(() => {
    console.log('handleLoadMore triggered', {
      currentPostsLength: posts.length,
      totalPosts,
      isLoading,
      hasReachedEnd
    });
    
    if (!isLoading && !hasReachedEnd) {
      console.log('Fetching more posts...');
      fetchMorePosts();
    }
  }, [fetchMorePosts, posts.length, totalPosts, isLoading, hasReachedEnd]);

  const initialLoad = useCallback(() => {
    console.log('Initial load triggered');
    fetchPosts(filters, 0, limit);
  }, [fetchPosts, filters, limit]);

  useEffect(() => {
    initialLoad();
  }, [initialLoad]);

  useEffect(() => {
    console.log('Filters changed:', filters);
    // Remove or comment out the extra fetch if not needed:
    // fetchPosts(filters, 0, limit);
  }, [filters]);

  useEffect(() => {
    const scrollContainer = loadMoreRef.current;
    if (!scrollContainer) return;

    const handleScroll = debounce(() => {
      const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
      const nearBottom = scrollHeight - (scrollTop + clientHeight) < 100;
      
      console.log('Scroll check:', {
        nearBottom,
        postsLength: posts.length,
        totalPosts,
        isLoading
      });

      if (nearBottom && !isLoading && posts.length < totalPosts) {
        handleLoadMore();
      }
    }, 200, { leading: true, trailing: true });

    scrollContainer.addEventListener('scroll', handleScroll);
    return () => {
      scrollContainer.removeEventListener('scroll', handleScroll);
      handleScroll.cancel();
    };
  }, [handleLoadMore, isLoading, posts.length, totalPosts]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setFilters((prev) => ({ ...prev, search_text: e.target.value }));
  };

  const debouncedHandleSearchChange = useMemo(() => debounce(handleSearchChange, 300), []);

  useEffect(() => {
    return () => {
      debouncedHandleSearchChange.cancel();
    };
  }, [debouncedHandleSearchChange]);

  const filteredPosts = useMemo(() => {
    return posts
      .filter((post) => {
        // Add null checks for all properties
        const titleMatch = post.title?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false;
        const tagMatch = filters.tag_name
          ? post.tags?.some((tag: string) => tag.toLowerCase().includes(filters.tag_name.toLowerCase())) ?? false
          : true;
        const statusMatch = filters.status === 'All' || (post.status?.toLowerCase().includes(filters.status.toLowerCase()) ?? false);
        const createdBeforeMatch = filters.created_before && post.createdAt
          ? new Date(post.createdAt) < new Date(filters.created_before)
          : true;
        const createdAfterMatch = filters.created_after && post.createdAt
          ? new Date(post.createdAt) > new Date(filters.created_after)
          : true;

        return titleMatch && tagMatch && statusMatch && createdBeforeMatch && createdAfterMatch;
      })
      .sort((a, b) => new Date(b.updatedAt || 0).getTime() - new Date(a.updatedAt || 0).getTime());
  }, [posts, searchTerm, filters]);

  const latestDate = filteredPosts.length > 0 ? new Date(filteredPosts[0].updatedAt) : null;

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleApplyFilters = () => {
    // Clean up filters before applying
    const cleanedFilters = Object.entries(filters).reduce((acc, [key, value]) => {
      if (value === '' || value === null || value === undefined) {
        return acc;
      }
      acc[key] = value;
      return acc;
    }, {} as Record<string, any>);

    setShowFilters(false);
    fetchPosts(cleanedFilters, 0, limit);
  };

  const handlePostSelect = (post: Post) => {
    setCurrentPost(post);
  };

  return (
    <div
      className="transition-all duration-300 bg-white dark:bg-gray-800 border-r flex flex-col h-full"
    >
      <EditorToolbar isCollapsed={isCollapsed} onToggleCollapse={onToggleCollapse} />
      {!isCollapsed && (
        <>
          <div className="p-4">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search posts..."
                value={searchTerm}
                onChange={debouncedHandleSearchChange}
                className="w-full pl-9 pr-4 py-2 bg-gray-100 dark:bg-gray-700 rounded"
              />
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                <Filter className="w-4 h-4" />
              </button>
            </div>
            {showFilters && (
              <div className="mt-2 space-y-3 p-4 bg-white dark:bg-gray-800 rounded-lg shadow">
                <div className="grid grid-cols-1 gap-3">
                  <div>
                    <label className="block text-sm font-medium mb-1">Title Contains</label>
                    <input
                      type="text"
                      name="title_contains"
                      value={filters.title_contains}
                      onChange={handleFilterChange}
                      className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Post Type</label>
                    <select
                      name="post_type"
                      value={filters.post_type}
                      onChange={handleFilterChange}
                      className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                    >
                      <option value="">All Types</option>
                      <option value="blog">Blog</option>
                      <option value="social">Social</option>
                      <option value="news">News</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Status</label>
                    <select
                      name="status"
                      value={filters.status}
                      onChange={handleFilterChange}
                      className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                    >
                      <option value="All">All</option>
                      <option value="Draft">Draft</option>
                      <option value="Published">Published</option>
                      <option value="Scheduled">Scheduled</option>
                      <option value="Archived">Archived</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Domain</label>
                    <input
                      type="text"
                      name="domain"
                      value={filters.domain}
                      onChange={handleFilterChange}
                      className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Tag Name</label>
                    <input
                      type="text"
                      name="tag_name"
                      value={filters.tag_name}
                      onChange={handleFilterChange}
                      className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Source Type</label>
                    <select
                      name="source_type"
                      value={filters.source_type}
                      onChange={handleFilterChange}
                      className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                    >
                      <option value="">All Sources</option>
                      <option value="web">Web</option>
                      <option value="twitter">Twitter</option>
                      <option value="rss">RSS</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-sm font-medium mb-1">Created After</label>
                      <input
                        type="datetime-local"
                        name="created_after"
                        value={filters.created_after || ''}
                        onChange={handleFilterChange}
                        className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">Created Before</label>
                      <input
                        type="datetime-local"
                        name="created_before"
                        value={filters.created_before || ''}
                        onChange={handleFilterChange}
                        className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-sm font-medium mb-1">Updated After</label>
                      <input
                        type="datetime-local"
                        name="updated_after"
                        value={filters.updated_after || ''}
                        onChange={handleFilterChange}
                        className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">Updated Before</label>
                      <input
                        type="datetime-local"
                        name="updated_before"
                        value={filters.updated_before || ''}
                        onChange={handleFilterChange}
                        className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Media Type</label>
                    <select
                      name="media_type"
                      value={filters.media_type}
                      onChange={handleFilterChange}
                      className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                    >
                      <option value="">All Media</option>
                      <option value="image">Image</option>
                      <option value="video">Video</option>
                      <option value="document">Document</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">URL Type</label>
                    <select
                      name="url_type"
                      value={filters.url_type}
                      onChange={handleFilterChange}
                      className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                    >
                      <option value="">All URLs</option>
                      <option value="article">Article</option>
                      <option value="blog">Blog</option>
                      <option value="social">Social</option>
                    </select>
                  </div>

                  <button
                    onClick={handleApplyFilters}
                    className="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
                  >
                    Apply Filters
                  </button>
                </div>
              </div>
            )}
          </div>
            <div 
              ref={loadMoreRef}
              className="flex-1 overflow-auto max-h-[calc(100vh-120px)]" // Set max height
            >
              {filteredPosts.length > 0 ? (
                filteredPosts.map((post) => (
                  <div className="relative border-b border-gray-200 dark:border-gray-700" key={post.id}>
                    <button
                      onClick={() => handlePostSelect(post)}
                      className={`w-full p-4 text-left hover:bg-gray-100 dark:hover:bg-gray-700 ${currentPost?.id === post.id ? 'bg-gray-100 dark:bg-gray-700' : ''}`}
                    >
                      <h3 className={`mb-1 ${latestDate && new Date(post.updatedAt).getDate() === latestDate.getDate() ? 'font-medium' : 'font-normal'}`}>
                        {post.title}
                      </h3>
                      <div className="flex justify-between items-center">
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {new Date(post.updatedAt).toLocaleDateString()}
                        </p>
                        <span
                          className={`inline-block px-2 py-1 text-xs font-semibold rounded ${
                            post.status === 'Published'
                              ? 'bg-green-100 text-green-800'
                              : post.status === 'Rejected'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
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
                ))
              ) : (
                <div className="p-4 text-center text-gray-500">
                  {isLoading ? 'Loading...' : 'No posts found'}
                </div>
              )}
              <div className="h-10 flex justify-center items-center">
                {isLoading && <Loader className="animate-spin" />}
                {hasReachedEnd && posts.length > 0 && (
                  <span className="text-sm text-gray-500">No more posts</span>
                )}
              </div>
            </div>
        </>
      )}
    </div>
  );
};