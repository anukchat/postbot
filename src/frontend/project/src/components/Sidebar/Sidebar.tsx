import React, { useState, useEffect, useRef } from 'react';
import {
  Search,
  Plus,
  Moon,
  Sun,
  Filter,
  ChevronRight,
  ChevronLeft
} from 'lucide-react';
import { useEditorStore } from '../../store/editorStore';
import { EditorToolbar } from '../Sidebar/EditorToolbar';

interface SidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isCollapsed, onToggleCollapse }) => {
  const { posts, currentPost, setCurrentPost, isDarkMode, toggleTheme, fetchPosts, skip, limit, totalPosts } = useEditorStore();
  const [searchTerm, setSearchTerm] = React.useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    search_text: '',
    tags: '',
    status: 'All',
    createdBefore: '',
    createdAfter: '',
  });
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    fetchPosts(filters, 0, limit);
  }, [fetchPosts, filters, limit]);

  useEffect(() => {
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    observerRef.current = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && skip + limit < totalPosts) {
        fetchPosts(filters, skip + limit, limit);
      }
    });

    if (loadMoreRef.current) {
      observerRef.current.observe(loadMoreRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [fetchPosts, filters, skip, limit, totalPosts]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setFilters((prev) => ({ ...prev, search_text: e.target.value }));
  };

  const filteredPosts = posts.filter((post) => {
    const titleMatch = post.title.toLowerCase().includes(searchTerm.toLowerCase());
    const tagMatch = filters.tags
      ? post.tags.some((tag: string) => tag.toLowerCase().includes(filters.tags.toLowerCase()))
      : true;
    const statusMatch = filters.status === 'All' || post.status.toLowerCase().includes(filters.status.toLowerCase());
    const createdBeforeMatch = filters.createdBefore
      ? new Date(post.createdAt) < new Date(filters.createdBefore)
      : true;
    const createdAfterMatch = filters.createdAfter
      ? new Date(post.createdAt) > new Date(filters.createdAfter)
      : true;

    return titleMatch && tagMatch && statusMatch && createdBeforeMatch && createdAfterMatch;
  });

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleApplyFilters = () => {
    setShowFilters(false);
    fetchPosts(filters, 0, limit);
  };

  return (
    <div
      className="transition-all duration-300 bg-white dark:bg-gray-800 border-r flex flex-col h-full"
      // style={{
      //   width: isCollapsed ? '3rem' /* Collapsed width */ : '20rem' /* Expanded width */,
      // }}
    >
      {/* Header Section */}
      <EditorToolbar isCollapsed={isCollapsed} onToggleCollapse={onToggleCollapse} />
      {/* Main Content Section */}
      {!isCollapsed && (
        <>
          <div className="p-4">
            {/* Search Bar */}
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search posts..."
                value={searchTerm}
                onChange={handleSearchChange}
                className="w-full pl-9 pr-4 py-2 bg-gray-100 dark:bg-gray-700 rounded"
              />
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                <Filter className="w-4 h-4" />
              </button>
            </div>

            {/* Filters Section */}
            {showFilters && (
              <div className="mt-2">
                <input
                  type="text"
                  name="search_text"
                  placeholder="Search Text"
                  value={filters.search_text}
                  onChange={handleFilterChange}
                  className="border p-2 rounded w-full mb-2"
                />
                <input
                  type="text"
                  name="tags"
                  placeholder="Tags"
                  value={filters.tags}
                  onChange={handleFilterChange}
                  className="border p-2 rounded w-full mb-2"
                />
                <select
                  name="status"
                  value={filters.status}
                  onChange={handleFilterChange}
                  className="border p-2 rounded w-full mb-2"
                >
                  <option value="All">All</option>
                  <option value="Draft">Draft</option>
                  <option value="Published">Published</option>
                  <option value="Scheduled">Scheduled</option>
                  <option value="Archived">Archived</option>
                  <option value="Rejected">Rejected</option>
                  <option value="Deleted">Deleted</option>
                </select>
                <input
                  type="date"
                  name="createdBefore"
                  value={filters.createdBefore}
                  onChange={handleFilterChange}
                  className="border p-2 rounded w-full mb-2"
                />
                <input
                  type="date"
                  name="createdAfter"
                  value={filters.createdAfter}
                  onChange={handleFilterChange}
                  className="border p-2 rounded w-full mb-2"
                />
                <button
                  onClick={handleApplyFilters}
                  className="bg-blue-500 text-white px-4 py-2 rounded w-full"
                >
                  Apply Filters
                </button>
              </div>
            )}
          </div>

            {/* Posts List */}
            <div className="flex-1 overflow-auto">
              {filteredPosts.map((post) => (
              <button
                key={post.id}
                onClick={() => setCurrentPost(post)}
                className={`w-full p-4 text-left hover:bg-gray-100 dark:hover:bg-gray-700 ${currentPost?.id === post.id ? 'bg-gray-100 dark:bg-gray-700' : ''
                }`}
              >
                <h3 className="font-medium mb-1">{post.title}</h3>
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
              ))}
              <div ref={loadMoreRef} className="h-10"></div>
            </div>
        </>
      )}
    </div>
  );
};
