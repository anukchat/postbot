import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import {
  Search,
  Filter,
  Loader // Add the Loader icon
} from 'lucide-react';
import { useEditorStore } from '../../store/editorStore';
import { EditorToolbar } from './EditorToolbar';
import debounce from 'lodash.debounce'; // Add this import
import { Post } from '../../types';

interface SidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

interface FilterState {
  post_type: string;
  status: string;
  domain: string;
  tag_name: string;
  created_after: string;
  created_before: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ isCollapsed, onToggleCollapse }) => {
  const { 
    posts, 
    currentPost, 
    setCurrentPost, 
    fetchPosts, 
    fetchMorePosts, 
    limit, 
    totalPosts, 
    isLoading,
    hasReachedEnd, 
  } = useEditorStore();
  const [searchTerm, setSearchTerm] = React.useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<FilterState>({
    post_type: '',
    status: '',
    domain: '',
    tag_name: '',
    created_after: '',
    created_before: ''
  });
  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  // Add a ref to track if initial fetch is done
  const initialFetchDoneRef = useRef(false);
  // Add a ref to track ongoing fetch
  const isFetchingRef = useRef(false);

  // Modify handleLoadMore to prevent duplicate calls
  const handleLoadMore = useCallback(() => {
    if (isFetchingRef.current || hasReachedEnd) {
      return;
    }

    isFetchingRef.current = true;
    fetchPosts({
      timestamp: Date.now(),
    }, posts.length, limit).finally(() => {
      isFetchingRef.current = false;
    });
  }, [fetchPosts, posts.length, hasReachedEnd, limit]);

  // Modify initial fetch useEffect
  useEffect(() => {
    if (!initialFetchDoneRef.current && !isLoading) {
      initialFetchDoneRef.current = true;
      fetchPosts({
        timestamp: Date.now(),
        forceRefresh: true
      }, 0, limit);
    }
  }, [fetchPosts, isLoading, limit]);

  // Remove the second fetch effect that was causing duplicate calls

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
  };

  // Modify scroll handler useEffect
  useEffect(() => {
    const scrollContainer = loadMoreRef.current;
    if (!scrollContainer) return;

    const handleScroll = debounce(() => {
      if (isFetchingRef.current || hasReachedEnd) return;

      const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
      const nearBottom = scrollHeight - (scrollTop + clientHeight) < 100;
      
      if (nearBottom && !isLoading && posts.length < totalPosts) {
        handleLoadMore();
      }
    }, 200);

    scrollContainer.addEventListener('scroll', handleScroll);
    return () => {
      scrollContainer.removeEventListener('scroll', handleScroll);
      handleScroll.cancel();
    };
  }, [handleLoadMore, isLoading, posts.length, totalPosts, hasReachedEnd]);

  const filteredPosts = useMemo(() => {
    return posts
      .filter((post) => {
        // Client-side filtering using searchTerm
        const titleMatch = searchTerm 
          ? post.title?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false
          : true;
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
    // Just update local state, don't trigger API call
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleApplyFilters = () => {
    // Clean up filters before applying
    const cleanedFilters = Object.entries(filters).reduce((acc, [key, value]) => {
      // Skip empty values and "All" status
      if (value === '' || value === null || value === undefined) {
        return acc;
      }
      acc[key] = value;
      return acc;
    }, {} as Record<string, any>);

    // Add search term if it exists
    if (searchTerm) {
      cleanedFilters.title_contains = searchTerm;
    }

    setShowFilters(false);
    fetchPosts(cleanedFilters, 0, limit);
  };

  const handlePostSelect = (post: Post) => {
    setCurrentPost(post);
  };

  return (
    <div className="transition-all duration-300 bg-white dark:bg-gray-800 border-r flex flex-col h-full relative">
      {/* <EditorToolbar isCollapsed={isCollapsed} onToggleCollapse={onToggleCollapse} /> */}
      {!isCollapsed && (
        <>
          <div className="p-4 border-b">
            <div className="relative border dark:border-gray-700 rounded-lg">
              <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
              type="text"
              placeholder="Search posts..."
              value={searchTerm}
              onChange={handleSearchChange}
              className="w-full pl-9 pr-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg border-0 focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-full transition-colors"
              >
                <Filter className="w-4 h-4" />
              </button>
            </div>
            
            {/* Filter Overlay */}
            {showFilters && (
              <div className="absolute z-10 left-4 right-4 mt-2 bg-white dark:bg-gray-800 rounded-xl shadow-lg border dark:border-gray-700 p-4">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Post Type</label>
                    <select
                      name="post_type"
                      value={filters.post_type}
                      onChange={handleFilterChange}
                      className="w-full p-2 rounded-lg bg-gray-50 dark:bg-gray-700 border-0 focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">All Types</option>
                      <option value="blog">Blog</option>
                      <option value="twitter_post">Twitter Post</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Status</label>
                    <select
                      name="status"
                      value={filters.status}
                      onChange={handleFilterChange}
                      className="w-full p-2 rounded-lg bg-gray-50 dark:bg-gray-700 border-0 focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">All Status</option>
                      <option value="draft">Draft</option>
                      <option value="published">Published</option>
                      <option value="scheduled">Scheduled</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Domain</label>
                    <input
                      type="text"
                      name="domain"
                      value={filters.domain}
                      onChange={handleFilterChange}
                      className="w-full p-2 rounded-lg bg-gray-50 dark:bg-gray-700 border-0 focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter domain..."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Tag</label>
                    <input
                      type="text"
                      name="tag_name"
                      value={filters.tag_name}
                      onChange={handleFilterChange}
                      className="w-full p-2 rounded-lg bg-gray-50 dark:bg-gray-700 border-0 focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter tag..."
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
                        className="w-full p-2 rounded-lg bg-gray-50 dark:bg-gray-700 border-0 focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">To</label>
                      <input
                        type="date"
                        name="created_before"
                        value={filters.created_before}
                        onChange={handleFilterChange}
                        className="w-full p-2 rounded-lg bg-gray-50 dark:bg-gray-700 border-0 focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>

                  <div className="flex gap-2 pt-2">
                    <button
                      onClick={() => {
                        setFilters({
                          post_type: '',
                          status: '',
                          domain: '',
                          tag_name: '',
                          created_after: '',
                          created_before: ''
                        });
                        setShowFilters(false);
                      }}
                      className="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      Reset
                    </button>
                    <button
                      onClick={handleApplyFilters}
                      className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                    >
                      Apply
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Continue with the existing posts list... */}
          <div ref={loadMoreRef} className="flex-1 overflow-auto max-h-[calc(100vh-120px)]">
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