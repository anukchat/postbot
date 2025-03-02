import { useState, useMemo, useRef, useEffect } from 'react';
import { Search, Filter, Sparkles, X, Loader2 } from 'lucide-react';
import { TemplateCard } from './TemplateCard';
import { useEditorStore } from '../../store/editorStore';
import { cacheService } from '../../services/cacheService';

interface Template {
  id: string;
  title: string;
  description: string;
  category: string;
}

interface TemplatesViewProps {
  onTemplateSelect: (template: Template) => void;
}

export const TemplatesView = ({ onTemplateSelect }: TemplatesViewProps) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const filtersRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Use editor store for templates
  const { templates, isTemplateLoading, fetchTemplates } = useEditorStore();

  // Add cache error state
  const [cacheError, setCacheError] = useState<string | null>(null);

  // Enhance useEffect for template fetching
  useEffect(() => {
    const loadTemplates = async () => {
      try {
        await fetchTemplates();
        // Clear any previous cache errors
        setCacheError(null);
      } catch (error) {
        console.error('Error loading templates:', error);
        setCacheError('Failed to load templates. Retrying...');
        // Retry once after cache failure
        try {
          cacheService.clearCache();
          await fetchTemplates();
          setCacheError(null);
        } catch (retryError) {
          setCacheError('Unable to load templates. Please try again later.');
        }
      }
    };

    loadTemplates();
  }, [fetchTemplates]);

  // Add cache stats monitoring (for development)
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      const stats = cacheService.getCacheStats();
      console.log('Cache stats:', stats);
    }
  }, [templates]);

  // Clear all filters
  const clearFilters = () => {
    setSelectedCategory('');
    setSearchTerm('');
  };

  // Close filters when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      
      if (filtersRef.current && 
          !filtersRef.current.contains(target) && 
          !target.closest('[data-filter-toggle]')) {
        setShowFilters(false);
      }
    };

    if (showFilters) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showFilters]);

  // Handle scroll behavior
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 100);
    };
    
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Filter templates locally
  const filteredTemplates = useMemo(() => {
    return templates.filter(template => {
      const matchesSearch = 
        template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (template.description || '').toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesCategory = !selectedCategory || 
        template.parameters.some(param => 
          param.name === 'content_type' && 
          param.values?.value === selectedCategory
        );

      return matchesSearch && matchesCategory;
    });
  }, [templates, searchTerm, selectedCategory]);

  // Extract unique categories from templates
  const availableCategories = useMemo(() => {
    const categories = new Set<string>();
    templates.forEach(template => {
      const contentTypeParam = template.parameters.find(p => p.name === 'content_type');
      if (contentTypeParam?.values?.value) {
        categories.add(contentTypeParam.values.value);
      }
    });
    return Array.from(categories);
  }, [templates]);

  const handleTemplateClick = (template: any) => {
    // Convert the template structure to match what NewBlogModal expects
    const contentTypeParam = template.parameters.find((p: { name: string; }) => p.name === 'content_type');
    const formattedTemplate = {
      id: template.template_id,
      title: template.name,
      description: template.description || '',
      category: contentTypeParam?.values?.value || ''
    };
    onTemplateSelect(formattedTemplate);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Fixed Search Bar with Backdrop */}
      <div className={`fixed top-0 left-16 right-0 z-[15] bg-white dark:bg-gray-800 shadow-sm transition-all duration-300 ease-out ${
        isScrolled 
          ? 'border-b border-gray-200 dark:border-gray-700' 
          : 'border-transparent'
      }`}>
        <div className="flex justify-center items-center px-4">
          <div 
            className="max-w-xl w-full relative animate-in fade-in slide-in-from-top-2 duration-700 ease-out"
            style={{ 
              paddingTop: isScrolled ? '0.75rem' : '1rem',
              paddingBottom: isScrolled ? '0.75rem' : '1rem'
            }}
          >
            {/* Search Bar Container */}
            <div className="relative">
              {/* Search Input with Icon */}
              <div className="relative">
                <input
                  ref={searchInputRef}
                  type="text"
                  placeholder={!selectedCategory ? "Search templates..." : "Search in category..."}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onFocus={() => setIsSearchFocused(true)}
                  onBlur={() => setIsSearchFocused(false)}
                  className={`w-full pl-10 pr-20 py-2.5 rounded-lg border-2 border-gray-200 bg-white hover:bg-white focus:bg-white dark:bg-gray-800 dark:hover:bg-gray-800 dark:focus:bg-gray-800 dark:border-gray-700 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-all will-change-[padding] duration-300 ease-out text-sm placeholder:text-gray-400`}
                  style={selectedCategory ? {
                    paddingLeft: 'calc(2.75rem + var(--chip-width, 0px))'
                  } : undefined}
                />
                
                {/* Search Icon */}
                <div className={`absolute left-3 top-1/2 -translate-y-1/2 transition-all duration-300 pointer-events-none z-10 ${
                  isTemplateLoading ? 'scale-110' : ''
                }`}>
                  {isTemplateLoading ? (
                    <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
                  ) : (
                    <Search className={`w-5 h-5 transition-colors duration-200 ${
                      isSearchFocused ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                    }`} />
                  )}
                </div>
                
                {/* Category Badge with auto-sizing */}
                {selectedCategory && (
                  <div className="absolute left-9 top-1/2 -translate-y-1/2 flex items-center z-20">
                    <span 
                      className="px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 dark:bg-blue-900/50 dark:text-blue-300 text-sm font-medium flex items-center gap-1 min-w-0 transition-all duration-300 ease-out will-change-[width]"
                      ref={node => {
                        if (node) {
                          requestAnimationFrame(() => {
                            const width = node.getBoundingClientRect().width;
                            document.documentElement.style.setProperty('--chip-width', `${width}px`);
                          });
                        }
                      }}
                    >
                      <span className="truncate">{selectedCategory}</span>
                      <button
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          searchInputRef.current?.focus();
                          document.documentElement.style.setProperty('--chip-width', '0px');
                          setTimeout(() => setSelectedCategory(''), 50);
                        }}
                        className="flex-shrink-0 p-0.5 hover:bg-blue-100 dark:hover:bg-blue-800 rounded-full transition-colors duration-200"
                        aria-label="Clear category filter"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </span>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className={`absolute right-4 top-1/2 transform -translate-y-1/2 flex items-center gap-1 transition-transform duration-300`}>
                {(selectedCategory || searchTerm) && (
                  <button
                    onClick={() => {
                      clearFilters();
                      searchInputRef.current?.focus();
                    }}
                    className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                    title="Clear filters"
                  >
                    <X className="w-4 h-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" />
                  </button>
                )}
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={`p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors ${
                    showFilters ? 'bg-gray-100 dark:bg-gray-700' : ''
                  }`}
                  title={showFilters ? "Hide filters" : "Show filters"}
                  data-filter-toggle
                >
                  <Filter 
                    className={`w-4 h-4 transition-colors duration-200 ${
                      showFilters || selectedCategory 
                        ? 'text-blue-500' 
                        : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
                    }`} 
                  />
                </button>
              </div>

              {/* Floating Filters Panel - Updated positioning and width */}
              {showFilters && (
                <div 
                  ref={filtersRef}
                  className="absolute left-0 right-0 mt-1 p-3 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200/60 dark:border-gray-700/60 transform-gpu transition-all duration-200 ease-out z-[20] max-h-[280px] overflow-y-auto animate-in fade-in slide-in-from-top-1"
                >
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => {
                        setSelectedCategory('');
                        setShowFilters(false);
                      }}
                      className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                        !selectedCategory 
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
                      }`}
                    >
                      All
                    </button>
                    {availableCategories.map((category) => (
                      <button
                        key={category}
                        onClick={() => {
                          setSelectedCategory(category);
                          setShowFilters(false);
                        }}
                        className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                          selectedCategory === category
                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
                        }`}
                      >
                        {category}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Remove the duplicate icons section */}
      <div className="relative z-[5] rounded-lg" style={{ marginTop: '64px' }}>
        {/* Hero Banner */}
        <div className="relative z-10 h-[360px] bg-gradient-to-br from-purple-600 via-blue-600 to-blue-700 overflow-hidden">
          {/* Decorative patterns */}
          <div className="absolute inset-0">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-600/20 via-blue-600/20 to-blue-700/20 backdrop-blur-3xl" />
            <div className="absolute inset-0" style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 .895-3 2 .895 2 2 2zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2z' fill='%23ffffff' fill-opacity='0.1' fill-rule='evenodd'/%3E%3C/svg%3E")`,
              backgroundSize: '30px 30px'
            }} />
          </div>

          {/* Content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center text-white text-center px-4 pb-16">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-8 h-8" />
              <span className="text-xl font-medium">Choose your template</span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-4 leading-tight">
              Create engaging content in minutes
            </h1>
            <p className="text-lg text-white/80 max-w-2xl">
              Choose from our collection of professionally designed templates and customize them to match your style
            </p>
          </div>

          {/* Bottom fade */}
          <div className="absolute bottom-0 left-0 right-0 h-48 bg-gradient-to-t from-gray-50 dark:from-gray-900 to-transparent" />
        </div>

        {/* Templates Grid - Adding background to create new stacking context */}
        <div className="relative z-10 max-w-[1600px] mx-auto px-6 py-8 -mt-20 bg-gray-50 dark:bg-gray-900">
          {isTemplateLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="aspect-[16/9] bg-gray-200 dark:bg-gray-700 rounded-t-xl" />
                  <div className="p-4 space-y-3 bg-white dark:bg-gray-800 rounded-b-xl border border-gray-200 dark:border-gray-700">
                    <div className="h-2 w-20 bg-gray-200 dark:bg-gray-700 rounded" />
                    <div className="h-4 w-3/4 bg-gray-200 dark:bg-gray-700 rounded" />
                    <div className="h-3 w-full bg-gray-200 dark:bg-gray-700 rounded" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {filteredTemplates.map((template) => (
                  <div 
                    key={template.template_id} 
                    className="transform cursor-pointer p-4 border rounded-lg hover:border-blue-500 transition-colors" 
                    style={{ transform: 'translate3d(0, 0, 0)' }}
                    onClick={() => handleTemplateClick(template)}
                  >
                    <TemplateCard
                      id={template.template_id}
                      title={template.name}
                      description={template.description || ''}
                      thumbnail={template.template_image_url || ''} // You might want to add a default image
                      category={template.parameters.find(p => p.name === 'content_type')?.values?.value || ''}
                    />
                  </div>
                ))}
              </div>

              {filteredTemplates.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-gray-500 dark:text-gray-400">
                    No templates found matching your criteria
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Add cache error message */}
      {cacheError && (
        <div className="fixed top-4 right-4 bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded shadow-lg z-50">
          <div className="flex items-center">
            <div className="py-1">
              <svg className="w-6 h-6 mr-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <p className="font-bold">Error</p>
              <p className="text-sm">{cacheError}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};