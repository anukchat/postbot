import { useState, useMemo, useRef, useEffect } from 'react';
import { Search, Filter, Sparkles, X, Loader2 } from 'lucide-react';
import { TemplateCard } from './TemplateCard';

// Updated categories
const TEMPLATE_CATEGORIES = [
  'Blog Post',
  'Product Review',
  'Tutorial',
  'Case Study',
  'Industry News',
  'Opinion Piece',
  'How-to Guide',
  'Comparison Article',
  'List Article',
  'Interview',
  'Research Summary',
  'Newsletter',
  'Social Media',
  'Personal Story',
  'Company Update',
  'Event Coverage',
  'Expert Analysis'
];

// Extended template list
const DUMMY_TEMPLATES = [
  {
    id: '1',
    title: 'Product Review Template',
    description: 'A comprehensive template for reviewing products with pros, cons, and detailed analysis.',
    thumbnail: 'https://images.unsplash.com/photo-1515378960530-7c0da6231fb1',
    category: 'Product Review'
  },
  {
    id: '2',
    title: 'How-to Guide Template',
    description: 'Step-by-step guide template with clear sections and explanations.',
    thumbnail: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3',
    category: 'How-to Guide'
  },
  {
    id: '3',
    title: 'Industry News Analysis',
    description: 'Template for analyzing and reporting on industry news and trends.',
    thumbnail: 'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f',
    category: 'Industry News'
  },
  {
    id: '4',
    title: 'Case Study Template',
    description: 'Structured template for presenting detailed case studies and success stories.',
    thumbnail: 'https://images.unsplash.com/photo-1605810230434-7631ac76ec81',
    category: 'Case Study'
  },
  {
    id: '5',
    title: 'Interview Article',
    description: 'Template for formatting expert interviews and Q&A sessions.',
    thumbnail: 'https://images.unsplash.com/photo-1521791136064-7986c2920216',
    category: 'Interview'
  },
  {
    id: '6',
    title: 'Research Summary',
    description: 'Template for summarizing and presenting research findings clearly.',
    thumbnail: 'https://images.unsplash.com/photo-1532619187608-e5375cab36aa',
    category: 'Research Summary'
  },
  {
    id: '7',
    title: 'Top 10 List Article',
    description: 'Template for creating engaging and informative list-based content.',
    thumbnail: 'https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b',
    category: 'List Article'
  },
  {
    id: '8',
    title: 'Technical Tutorial',
    description: 'Detailed template for technical how-to guides and tutorials.',
    thumbnail: 'https://images.unsplash.com/photo-1517180102446-f3ece451e9d8',
    category: 'Tutorial'
  },
  {
    id: '9',
    title: 'Newsletter Roundup',
    description: 'Weekly digest template perfect for curating and summarizing content for your audience.',
    thumbnail: 'https://images.unsplash.com/photo-1586339949216-35c2747cc36d',
    category: 'Newsletter'
  },
  {
    id: '10',
    title: 'Social Media Success Story',
    description: 'Template for showcasing social media campaign results and strategies.',
    thumbnail: 'https://images.unsplash.com/photo-1611926653458-09294b3142bf',
    category: 'Social Media'
  },
  {
    id: '11',
    title: 'Personal Journey Blog',
    description: 'Engaging template for sharing personal experiences and lessons learned.',
    thumbnail: 'https://images.unsplash.com/photo-1512245570155-d0d910ec9bc5',
    category: 'Personal Story'
  },
  {
    id: '12',
    title: 'Monthly Company Update',
    description: 'Professional template for sharing company news, milestones, and achievements.',
    thumbnail: 'https://images.unsplash.com/photo-1553484771-048eacb424b3',
    category: 'Company Update'
  },
  {
    id: '13',
    title: 'Conference Coverage',
    description: 'Template for comprehensive event reporting and key takeaways.',
    thumbnail: 'https://images.unsplash.com/photo-1475721027785-f74eccf877e2',
    category: 'Event Coverage'
  },
  {
    id: '14',
    title: 'Expert Opinion Piece',
    description: 'Template for in-depth analysis and professional insights on industry topics.',
    thumbnail: 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40',
    category: 'Expert Analysis'
  },
  {
    id: '15',
    title: 'Product Comparison Guide',
    description: 'Side-by-side comparison template for evaluating multiple products or services.',
    thumbnail: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f',
    category: 'Comparison Article'
  },
  {
    id: '16',
    title: 'Quick Tips & Tricks',
    description: 'Concise template for sharing quick, actionable advice and tips.',
    thumbnail: 'https://images.unsplash.com/photo-1586281380117-5a60ae2050cc',
    category: 'How-to Guide'
  }
];

export const TemplatesView = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const filtersRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const searchTimeoutRef = useRef<NodeJS.Timeout>();

  // Clear all filters
  const clearFilters = () => {
    setSelectedCategory('');
    setSearchTerm('');
  };

  // Close filters when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      
      // Check if click is outside the filters panel and not on the filter button
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

  // Debounced search with loading state
  useEffect(() => {
    setIsSearching(true);
    searchTimeoutRef.current = setTimeout(() => {
      setIsSearching(false);
    }, 300);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchTerm, selectedCategory]);

  // Handle scroll behavior
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 100);
    };
    
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const filteredTemplates = useMemo(() => {
    return DUMMY_TEMPLATES.filter(template => {
      const matchesSearch = template.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          template.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = !selectedCategory || template.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [searchTerm, selectedCategory]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Fixed Search Bar with Backdrop */}
      <div 
        className={`fixed top-0 left-16 right-0 z-[15] bg-white dark:bg-gray-800 shadow-sm transition-all duration-300 ease-out ${
          isScrolled 
            ? 'border-b border-gray-200 dark:border-gray-700' 
            : 'border-transparent'
        }`}
      >
        <div 
          className="max-w-xl mx-auto relative animate-in fade-in slide-in-from-top-2 duration-700 ease-out"
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
                isSearching ? 'scale-110' : ''
              }`}>
                {isSearching ? (
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
          </div>

          {/* Floating Filters Panel */}
          {showFilters && (
            <div 
              ref={filtersRef}
              className="absolute left-0 right-0 mt-2 p-3 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200/60 dark:border-gray-700/60 transform-gpu transition-all duration-200 ease-out z-[20] max-h-[280px] overflow-y-auto animate-in fade-in slide-in-from-top-1 duration-200"
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
                {TEMPLATE_CATEGORIES.map((category) => (
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

      {/* Content with refined spacing */}
      <div className="relative z-[5] rounded-lg" style={{ marginTop: '64px' }}>
        {/* Hero Banner */}
        <div className="relative z-10 h-[360px] bg-gradient-to-br from-purple-600 via-blue-600 to-blue-700 overflow-hidden">
          {/* Decorative patterns */}
          <div className="absolute inset-0">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-600/20 via-blue-600/20 to-blue-700/20 backdrop-blur-3xl" />
            <div className="absolute inset-0" style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 .895-3 2 .895 2 2 2zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 2 .895 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2z' fill='%23ffffff' fill-opacity='0.1' fill-rule='evenodd'/%3E%3C/svg%3E")`,
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
          {isSearching ? (
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
                  <div key={template.id} className="transform" style={{ transform: 'translate3d(0, 0, 0)' }}>
                    <TemplateCard {...template} />
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
    </div>
  );
};