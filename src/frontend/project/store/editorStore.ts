import { create } from 'zustand';
import { templateApi, deleteContent, filterContent, generatePostStream } from '../services/api';
import { Post } from '../types/editor';
import api from '../services/api';
import { cacheManager } from '../services/cacheManager';

// Add new interface for generation jobs
interface GenerationJob {
  thread_id: string;
  progress: string;
  status: 'initializing' | 'running' | 'completed' | 'failed' | 'cancelled';
  startTime: number;
  reader?: ReadableStreamDefaultReader<Uint8Array>;
  post_types: string[];
  notificationShown?: boolean; // Add this field to track notification state
}

export interface TemplateParameterValue {
  value_id: string;
  value: string;
  display_order?: number;
  created_at?: string;
}

export interface TemplateParameter {
  parameter_id: string;
  name: string;
  display_name: string;
  description?: string;
  is_required: boolean;
  created_at?: string;
  values: TemplateParameterValue;
}

export interface Template {
  template_id: string;
  name: string;
  description?: string;
  template_type: string;
  template_image_url?: string;
  parameters: TemplateParameter[];
  created_at: string;
  updated_at: string;
  is_deleted?: boolean;
}

export interface CreateTemplatePayload {
  name: string;
  description?: string;
  template_type: string;
  template_image_url?: string;
  parameters: TemplateParameter[];
}

export interface TemplateFilter {
  name?: string;
  template_type?: string;
  parameter_id?: string;
  value_id?: string;
  is_deleted?: boolean;
}

export interface Parameter {
  parameter_id: string;
  name: string;
  display_name: string;
  description?: string;
  is_required: boolean;
  created_at: string;
  values: ParameterValue[];
}

export interface ParameterValue {
  value_id: string;
  value: string;
  display_order: number;
  created_at: string;
}

export interface CachedTemplateData {
  templates: Template[];
  timestamp: number;
  filter?: TemplateFilter;
}

interface GeneratePayload {
  post_types?: string[];
  thread_id?: string;
  url?: string;
  tweet_id?: string;
}

// Base state interface for editor functionality
interface EditorState {
  posts: Post[];
  currentPost: Post | null;
  isDarkMode: boolean;
  isLoading: boolean;
  error: string | null;
  history: string[];
  future: string[];
  isContentUpdated: boolean;
  skip: number;
  limit: number;
  totalPosts: number;
  lastLoadedSkip: number;
  hasReachedEnd: boolean;
  lastRefreshTimestamp: number;
  trendingBlogTopics: string[];
  isListLoading: boolean;
  currentTab: 'blog' | 'twitter' | 'linkedin';
  
  // New properties for non-blocking generation
  runningGenerations: Record<string, GenerationJob>;
  hasRunningGenerations: boolean;
  
  setCurrentTab: (tab: 'blog' | 'twitter' | 'linkedin') => void;
  setCurrentPost: (post: Post | null) => void;
  toggleTheme: () => void;
  setPosts: (posts: Post[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  fetchPosts: (filters: any, skip?: number, limit?: number) => Promise<void>;
  fetchMorePosts: () => Promise<void>;
  updateContent: (content: string) => void;
  updateTwitterPost: (twitter_post: string) => void;
  updateLinkedinPost: (linkedin_post: string) => void;
  savePost: () => Promise<void>;
  publishPost: () => Promise<void>;
  rejectPost: () => Promise<void>;
  downloadMarkdown: () => void;
  prependMetadata: (content: string) => string;
  undo: (selected_tab: string) => void;
  redo: (selected_tab: string) => void;
  schedulePost: (post: Post, platform: string, date: Date) => void;
  fetchContentByThreadId: (thread_id: string, post_type?: string) => Promise<void>;
  generatePost: (post_types: string[], thread_id: string, payload?: GeneratePayload) => Promise<string>;
  cancelGeneration: (thread_id: string) => Promise<void>;
  clearCompletedGenerations: () => void;
  fetchTrendingBlogTopics: (subreddits?: string[], limit?: number) => Promise<void>;
  deletePost: (threadId: string) => Promise<void>;

  // Keep this but repurpose it for the most recent update from any generation
  generationProgress: string;
  setGenerationProgress: (progress: string) => void;
}

// Separate admin state interface
interface AdminState {
  templates: Template[];
  isTemplateLoading: boolean;
  parameters: Parameter[];
  parameterValues: Record<string, ParameterValue[]>;
  isParametersLoading: boolean;
  parametersError: string | null;
  isAdminView: boolean;
  isTemplateActionLoading: boolean;
  templateError: string | null;
  currentTemplate: Template | null;
  setIsAdminView: (isAdmin: boolean) => void;
  setTemplateError: (error: string | null) => void;
  fetchTemplates: (skip?: number, limit?: number, filter?: TemplateFilter, forceRefresh?: boolean) => Promise<void>;
  fetchParameters: () => Promise<void>;
  createTemplate: (template: CreateTemplatePayload) => Promise<void>;
  updateTemplate: (templateId: string, template: Partial<CreateTemplatePayload>) => Promise<void>;
  deleteTemplate: (templateId: string) => Promise<void>;
  createParameter: (parameter: Omit<Parameter, 'parameter_id' | 'created_at'>) => Promise<void>;
  updateParameter: (parameterId: string, parameter: Partial<Parameter>) => Promise<void>;
  deleteParameter: (parameterId: string) => Promise<void>;
  createParameterValue: (parameterId: string, value: Omit<ParameterValue, 'value_id' | 'created_at'>) => Promise<void>;
  updateParameterValue: (parameterId: string, valueId: string, value: Partial<ParameterValue>) => Promise<void>;
  deleteParameterValue: (parameterId: string, valueId: string) => Promise<void>;
  fetchParameterValues: (parameterId: string) => Promise<void>;
  handleUpdateTemplate: (templateId: string) => Promise<void>;
}

interface CombinedState extends EditorState, AdminState {}

export const useEditorStore = create<CombinedState>((set, get) => ({
  posts: [],
  currentPost: null,
  isDarkMode: false,
  isLoading: false,
  error: null,
  history: [],
  future: [],
  isContentUpdated: false,
  skip: 0,
  limit: 20,
  totalPosts: 0,
  currentTab: 'blog',
  lastLoadedSkip: -1,
  hasReachedEnd: false,
  lastRefreshTimestamp: Date.now(),
  isListLoading: false,
  trendingBlogTopics: [],
  templates: [],
  isTemplateLoading: false,
  parameters: [],
  parameterValues: {},
  isParametersLoading: false,
  parametersError: null,
  isAdminView: false,
  isTemplateActionLoading: false,
  templateError: null,
  currentTemplate: null,
  generationProgress: '',
  
  // Initialize new state for background generations
  runningGenerations: {},
  hasRunningGenerations: false,
  
  setGenerationProgress: (progress) => set({ generationProgress: progress }),

  setCurrentTab: (tab) => set({ currentTab: tab }),
  setCurrentPost: (post) => set({ currentPost: post }),
  toggleTheme: () => set((state) => ({ isDarkMode: !state.isDarkMode })),
  setPosts: (posts) => set({ posts }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  
  fetchPosts: async (filters, skip = 0, limit = 20) => {
    console.log('fetchPosts called', { filters, skip, limit });
    const { isLoading, hasReachedEnd } = get();
    
    // Do not fetch if already loading or reached end (unless explicitly requested to refresh)
    if (isLoading || (!filters.forceRefresh && !filters.reset && hasReachedEnd)) {
      console.log('Skip fetch - loading or reached end:', { isLoading, hasReachedEnd });
      return;
    }

    // Remove control flags from filters before sending to API
    const {
      forceRefresh,
      reset,
      noCache,
      timestamp,
      ...apiFilters
    } = filters;

    // Ensure apiFilters is a plain object without undefined/null values
    const cleanedFilters = Object.entries(apiFilters).reduce((acc, [key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        // Handle special cases like dates
        if (value instanceof Date) {
          acc[key] = value.toISOString();
        } else {
          acc[key] = value;
        }
      }
      return acc;
    }, {} as Record<string, any>);

    // Create a cache key based on filters and pagination
    const cacheKey = JSON.stringify({ filters: cleanedFilters, skip, limit });
    
    // Check if we have a valid cache entry and no force refresh requested
    if (!forceRefresh && !noCache) {
      const cachedData = cacheManager.getContentFromCache(cacheKey);
      if (cachedData) {
        console.log('Using cached content data');
        set({ 
          posts: cachedData.posts,
          totalPosts: cachedData.totalPosts,
          lastLoadedSkip: skip + cachedData.posts.length,
          hasReachedEnd: cachedData.posts.length < limit,
          isListLoading: false
        });
        return;
      }
    }

    // Set list loading instead of general loading
    set({ isListLoading: true });

    try {
      // Use the dedicated filterContent function with cleaned filters
      const response = await filterContent(cleanedFilters, skip, limit);
      console.log('API Response:', response.data);
      
      if (response.data && response.data.items) {
        const formattedBlogs = response.data.items.map((item: any) => ({
          id: item.id,
          thread_id: item.thread_id,
          title: item.title,
          content: item.content,
          twitter_post: item.twitter_post || '',
          linkedin_post: item.linkedin_post || '',
          status: item.status || 'Draft',
          tags: item.tags || [],
          createdAt: item.createdAt,
          updatedAt: item.updatedAt,
          urls: item.urls || [],
          media: item.media || [],
          source_type: item.source_type,
          source_identifier: item.source_identifier
        }));

        console.log('Formatted blogs:', formattedBlogs);
        
        // Set hasReachedEnd if we got fewer items than requested
        const newHasReachedEnd = formattedBlogs.length < limit;
        
        // Cache this result
        cacheManager.setContentInCache(cacheKey, formattedBlogs, response.data.total || formattedBlogs.length);
        
        set(state => {
          return {
            posts: filters.reset ? formattedBlogs : 
                  skip === 0 ? formattedBlogs : 
                  [...state.posts, ...formattedBlogs],
            totalPosts: response.data.total || formattedBlogs.length,
            lastLoadedSkip: skip + formattedBlogs.length,
            hasReachedEnd: newHasReachedEnd,
            isListLoading: false
          };
        });
      }
    } catch (error: any) {
      console.error('Error fetching blogs:', error);
      set({ isListLoading: false, isLoading: false, error: 'Error fetching blogs' });
    }
  },

  fetchMorePosts: async () => {
    const { fetchPosts, skip, limit, posts, totalPosts, isLoading, hasReachedEnd } = get();
    
    if (isLoading || hasReachedEnd) {
      console.log('Skip fetchMorePosts:', { isLoading, hasReachedEnd, postsLength: posts.length });
      return;
    }

    const remainingItems = totalPosts - posts.length;
    if (remainingItems <= 0) {
      set({ hasReachedEnd: true });
      return;
    }

    const nextLimit = Math.min(limit, remainingItems);
    console.log('Fetching next page:', { 
      skip, 
      nextLimit, 
      remainingItems,
      currentCount: posts.length,
      totalPosts 
    });

    await fetchPosts({}, skip, nextLimit);
  },

  updateContent: (content: string) => {
    console.log('Updating content:', { content });
    set((state) => {
      if (!state.currentPost) {
        console.error('No current post found');
        return state;
      }

      const updatedPost = {
        ...state.currentPost,
        content,
        updatedAt: new Date().toISOString(),
      };

      console.log('Updated post:', updatedPost);

      return {
        ...state,
        currentPost: updatedPost,
        history: [...state.history, state.currentPost.content],
        future: [],
        isContentUpdated: true,
      };
    });
  },

  updateTwitterPost: (twitter_post: string) => {
    console.log('Updating Twitter post:', { twitter_post });
    set((state) => {
      if (!state.currentPost) {
        console.error('No current post found');
        return state;
      }

      const updatedPost = {
        ...state.currentPost,
        twitter_post,
        updatedAt: new Date().toISOString(),
      };

      console.log('Updated post:', updatedPost);

      return {
        ...state,
        currentPost: updatedPost,
        history: [...state.history, state.currentPost.twitter_post || ''],
        future: [],
        isContentUpdated: true,
      };
    });
  },

  updateLinkedinPost: (linkedin_post: string) => {
    console.log('Updating LinkedIn post:', { linkedin_post });
    set((state) => {
      if (!state.currentPost) {
        console.error('No current post found');
        return state;
      }

      const updatedPost = {
        ...state.currentPost,
        linkedin_post,
        updatedAt: new Date().toISOString(),
      };

      console.log('Updated post:', updatedPost);

      return {
        ...state,
        currentPost: updatedPost,
        history: [...state.history, state.currentPost.linkedin_post || ''],
        future: [],
        isContentUpdated: true,
      };
    });
  },

  undo: (selected_tab: string) => {
    set((state) => {
      if (state.history.length === 0) return state;

      const previousContent = state.history[state.history.length - 1];
      const newHistory = state.history.slice(0, -1);

      if (selected_tab === 'blog') {
        return {
          ...state,
          currentPost: state.currentPost
            ? { ...state.currentPost, content: previousContent }
            : null,
          history: newHistory,
          future: [state.currentPost?.content || '', ...state.future],
          isContentUpdated: true,
        };
      } else if (selected_tab === 'twitter') {
        return {
          ...state,
          currentPost: state.currentPost
            ? { ...state.currentPost, twitter_post: previousContent }
            : null,
          history: newHistory,
          future: [state.currentPost?.twitter_post || '', ...state.future],
          isContentUpdated: true,
        };
      } else if (selected_tab === 'linkedin') {
        return {
          ...state,
          currentPost: state.currentPost
            ? { ...state.currentPost, linkedin_post: previousContent }
            : null,
          history: newHistory,
          future: [state.currentPost?.linkedin_post || '', ...state.future],
          isContentUpdated: true,
        };
      }
      return state;
    });
  },

  schedulePost: async (post, platform, date) => {
    if (!post.thread_id) return;
    
    try {
        const response = await api.put(`/content/thread/${post.thread_id}/schedule`, {
            status: 'scheduled',
            schedule_date: date.toISOString(),
            platform
        });

        if (response.data.success) {
            set((state) => ({
                currentPost: state.currentPost ? {
                    ...state.currentPost,
                    status: 'Scheduled'
                } : null
            }));
        }
    } catch (error) {
        console.error('Failed to schedule post:', error);
    }
},

  redo: (selected_tab: string) => {
    set((state) => {
      if (state.future.length === 0) return state;

      const nextContent = state.future[0];
      const newFuture = state.future.slice(1);

      if (selected_tab === 'blog') {
        return {
          ...state,
          currentPost: state.currentPost
            ? { ...state.currentPost, content: nextContent }
            : null,
          history: [...state.history, state.currentPost?.content || ''],
          future: newFuture,
          isContentUpdated: true,
        };
      } else if (selected_tab === 'twitter') {
        return {
          ...state,
          currentPost: state.currentPost
            ? { ...state.currentPost, twitter_post: nextContent }
            : null,
          history: [...state.history, state.currentPost?.twitter_post || ''],
          future: newFuture,
          isContentUpdated: true,
        };
      } else if (selected_tab === 'linkedin') {
        return {
          ...state,
          currentPost: state.currentPost
            ? { ...state.currentPost, linkedin_post: nextContent }
            : null,
          history: [...state.history, state.currentPost?.linkedin_post || ''],
          future: newFuture,
          isContentUpdated: true,
        };
      }
      return state;
    });
  },

  savePost: async () => {
    const { currentPost } = get();
    if (!currentPost) return;

    try {
        set({ isLoading: true });
        const response = await api.put(`/content/thread/${currentPost.thread_id}/save`, {
            title: currentPost.title,
            content: currentPost.content,
            twitter_post: currentPost.twitter_post,
            linkedin_post: currentPost.linkedin_post,
            status: 'Draft'
        });

        if (response.data) {
            set({ isLoading: false, error: null, isContentUpdated: false });
        }
    } catch (error) {
        set({ isLoading: false, error: 'Failed to save post' });
        console.error('Error saving post:', error);
    }
},

  publishPost: async () => {
    const { currentPost, fetchPosts } = get();
    if (!currentPost?.thread_id) return;

    try {
        set({ isLoading: true });
        const response = await api.put(`/content/thread/${currentPost.thread_id}/save`, {
          ...currentPost,
          status: 'Published'
        });

        if (response.data) {
            set({ isLoading: false, error: null, isContentUpdated: false });
            await fetchPosts({}); 
        }
    } catch (error) {
        set({ isLoading: false, error: 'Failed to publish post' });
        console.error('Error publishing post:', error);
    }
},

  rejectPost: async () => {
    const { currentPost, fetchPosts } = get();
    if (!currentPost?.thread_id) return;

    try {
        set({ isLoading: true });
        const response = await api.put(`/content/thread/${currentPost.thread_id}/save`, {
          ...currentPost,
          status: 'Rejected'
        });

        if (response.data) {
            set({ isLoading: false, error: null, isContentUpdated: false });
            await fetchPosts({}); 
        }
    } catch (error) {
        set({ isLoading: false, error: 'Failed to reject post' });
        console.error('Error rejecting post:', error);
    }
},

  downloadMarkdown: () => {
    const { currentPost } = get();
    if (!currentPost) return;

    const content = currentPost.content;
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentPost.title || 'untitled'}.md`;
    a.click();
    URL.revokeObjectURL(url);
  },

  prependMetadata: (content: string) => {
    const { currentPost } = get();
    if (!currentPost) return content;

    const frontmatter = `---
blogpost: true
date: ${currentPost.createdAt}
author: Anukool Chaturvedi
tags: ${currentPost.tags.join(', ')}
language: English
excerpt: 1...
---

${content}`;
    return frontmatter;
  },

  fetchContentByThreadId: async (thread_id: string, post_type?: string) => {
    set({ isLoading: true });
    try {
      const postTypeMap = {
        'linkedin': 'linkedin',
        'twitter': 'twitter',
        'blog': 'blog'
      };
      
      const params = post_type ? { post_type: postTypeMap[post_type as keyof typeof postTypeMap] } : undefined;
      const response = await api.get(`/content/thread/${thread_id}`, { params });
      if (response.data) {
        const currentState = get().currentPost || {};
        let updatedPost;

        if (post_type === 'linkedin') {
          updatedPost = { ...currentState, linkedin_post: response.data.content };
        } else if (post_type === 'twitter') {
          updatedPost = { ...currentState, twitter_post: response.data.content };
        } else {
          updatedPost = response.data;
        }

        set({ currentPost: updatedPost, isLoading: false, error: null });
      }
    } catch (error: any) {
      console.error('Error fetching content by thread_id:', error);
      set({ isLoading: false, error: 'Error fetching content' });
    }
  },

  // Updated generatePost method to be non-blocking
  generatePost: async (post_types: string[], thread_id: string, payload?: GeneratePayload) => {
    // Create a unique ID for this generation if thread_id isn't provided
    const generationId = thread_id || `gen_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    
    // Add entry to running generations map
    set((state: CombinedState) => {
      const newRunningGenerations = { 
        ...state.runningGenerations,
        [generationId]: {
          thread_id: generationId,
          progress: 'Initializing generation...',
          status: 'initializing' as const,
          startTime: Date.now(),
          post_types
        }
      };
      
      return { 
        runningGenerations: newRunningGenerations,
        hasRunningGenerations: true,
        generationProgress: 'Initializing generation...'
      };
    });
    
    let reader: ReadableStreamDefaultReader<Uint8Array> | undefined;
    try {
      let payloadData: any = { 
        post_types: post_types.map(type => type === 'twitter' ? 'twitter' : type === 'linkedin' ? 'linkedin' : type),
        thread_id: generationId,
        ...payload
      };

      // Use the streaming endpoint but don't block UI interaction
      reader = await generatePostStream(payloadData);
      if (!reader) {
        throw new Error('Failed to initialize content generation stream');
      }
      
      // Store reader reference to allow cancellation
      set((state: CombinedState) => ({
        runningGenerations: {
          ...state.runningGenerations,
          [generationId]: {
            ...state.runningGenerations[generationId],
            reader,
            status: 'running' as const
          }
        }
      }));
      
      // Process the stream in the background
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        // Convert the Uint8Array to text
        const text = new TextDecoder().decode(value);
        const lines = text.split('\n').filter(line => line.trim() !== '');
        
        for (const line of lines) {
          try {
            // Parse the JSON from the line
            const eventData = JSON.parse(line);
            
            // Update progress for this specific generation
            if (eventData.message) {
              set((state: CombinedState) => ({
                runningGenerations: {
                  ...state.runningGenerations,
                  [generationId]: {
                    ...state.runningGenerations[generationId],
                    progress: eventData.message
                  }
                },
                generationProgress: eventData.message
              }));
            } else if (eventData.node) {
              const progressInfo = eventData.progress ? ` (${eventData.progress}%)` : '';
              const progressMessage = `${eventData.status} ${eventData.node}${progressInfo}`;
              
              set((state: CombinedState) => ({
                runningGenerations: {
                  ...state.runningGenerations,
                  [generationId]: {
                    ...state.runningGenerations[generationId],
                    progress: progressMessage
                  }
                },
                generationProgress: progressMessage
              }));
            }
          } catch (err) {
            console.warn('Error parsing stream event:', err);
            // If line is not valid JSON but has content, show it as progress
            if (line.trim()) {
              const progressMessage = line;
              set((state: CombinedState) => ({
                runningGenerations: {
                  ...state.runningGenerations,
                  [generationId]: {
                    ...state.runningGenerations[generationId],
                    progress: progressMessage
                  }
                },
                generationProgress: progressMessage
              }));
            }
          }
        }
      }

      // After streaming is complete, mark as completed
      set((state: CombinedState) => ({
        runningGenerations: {
          ...state.runningGenerations,
          [generationId]: {
            ...state.runningGenerations[generationId],
            status: 'completed' as const,
            progress: 'Generation completed successfully.'
          }
        }
      }));
      
      // Return the generated post ID so it can be used for navigation
      return generationId;

    } catch (error: any) {
      console.error('Error generating post:', error);
      
      // Update the error state for this specific generation
      set((state: CombinedState) => ({
        runningGenerations: {
          ...state.runningGenerations,
          [generationId]: {
            ...state.runningGenerations[generationId],
            status: 'failed' as const,
            progress: error.message || 'Error generating post'
          }
        },
        error: error.message || 'Error generating post'
      }));
      
      throw error;
    }
  },
  
  // New method to cancel a generation in progress
  cancelGeneration: async (thread_id: string) => {
    const { runningGenerations } = get();
    const generation = runningGenerations[thread_id];
    
    if (!generation) return;
    
    if (generation.reader) {
      try {
        await generation.reader.cancel();
      } catch (e) {
        console.error('Error canceling reader:', e);
      }
    }
    
    set((state: CombinedState) => {
      const updatedGenerations = {
        ...state.runningGenerations,
        [thread_id]: {
          ...state.runningGenerations[thread_id],
          status: 'cancelled' as const,
          progress: 'Generation cancelled by user.'
        }
      };
      
      const hasActive = Object.values(updatedGenerations).some(g => 
        g.status === 'initializing' || g.status === 'running'
      );
      
      return {
        runningGenerations: updatedGenerations,
        hasRunningGenerations: hasActive
      };
    });
  },
  
  // Method to clean up completed/failed/cancelled generations from the UI
  clearCompletedGenerations: () => {
    set((state: CombinedState) => {
      const activeGenerations: Record<string, GenerationJob> = {};
      
      // Only keep active generations
      Object.entries(state.runningGenerations).forEach(([id, gen]) => {
        if (gen.status === 'initializing' || gen.status === 'running') {
          activeGenerations[id] = gen;
        }
      });
      
      return {
        runningGenerations: activeGenerations,
        hasRunningGenerations: Object.keys(activeGenerations).length > 0
      };
    });
  },

  fetchTrendingBlogTopics: async (subreddits?: string[], limit: number = 15) => {
    set({ trendingBlogTopics: [] });

    const cacheKey = subreddits ? subreddits.join(',') : 'all';
    const cachedTopics = cacheManager.getTrendingTopicsFromCache(cacheKey);
    
    if (cachedTopics) {
      set({ trendingBlogTopics: cachedTopics });
      return;
    }

    try {
      const params: Record<string, any> = { limit };
      if (subreddits && subreddits.length > 0) {
        params.subreddits = subreddits.join(',');
      }

      const response = await api.get('/reddit/topic-suggestions', { params });
      if (response.data?.content_ideas) {
        cacheManager.setTrendingTopicsInCache(cacheKey, response.data.content_ideas);
        set({ trendingBlogTopics: response.data.content_ideas });
      }
    } catch (error) {
      console.error('Error fetching trending blog topics:', error);
      set({ trendingBlogTopics: [] });
    }
  },

  // Admin Actions
  setIsAdminView: (isAdmin) => set({ isAdminView: isAdmin }),
  setTemplateError: (error) => set({ templateError: error }),

  handleUpdateTemplate: async (templateId: string) => {
    const { isTemplateActionLoading } = get();
    if (isTemplateActionLoading) return;

    set({ isTemplateActionLoading: true, templateError: null });

    try {
      const response = await templateApi.getTemplate(templateId);
      const template: Template = response.data;
      
      // Update state with properly typed template
      set((state) => ({
        ...state,
        currentTemplate: template,
        templates: state.templates.map(t => 
          t.template_id === templateId ? template : t
        )
      }));

    } catch (error) {
      set({ templateError: error instanceof Error ? error.message : 'An error occurred' });
    } finally {
      set({ isTemplateActionLoading: false });
    }
  },

  fetchTemplates: async (skip = 0, limit = 10, filter?: TemplateFilter, forceRefresh = false) => {
    const cacheKey = JSON.stringify({ skip, limit, filter: filter || {} });
    
    if (!forceRefresh) {
      const cachedData = cacheManager.getTemplatesFromCache(cacheKey);
      if (cachedData) {
        console.log('Using cached templates data');
        set({ templates: cachedData.templates });
        return;
      }
    }
    
    try {
      set({ isTemplateLoading: true, templateError: null });
      const response = await templateApi.getAllTemplates({ skip, limit }, filter);
      if (response.data) {
        cacheManager.setTemplatesInCache(cacheKey, response.data, filter);
        set({ templates: response.data });
      }
    } catch (error) {
      set({ templateError: error instanceof Error ? error.message : 'An error occurred' });
    } finally {
      set({ isTemplateLoading: false });
    }
  },

  createTemplate: async (template: CreateTemplatePayload) => {
    try {
      set({ isTemplateActionLoading: true, templateError: null });
      const response = await templateApi.createTemplate(template);
      if (response.data) {
        const templates = get().templates;
        set({ templates: [...templates, response.data] });
      }
      return response.data;
    } catch (error) {
      set({ templateError: error instanceof Error ? error.message : 'An error occurred' });
      throw error;
    } finally {
      set({ isTemplateActionLoading: false });
    }
  },

  updateTemplate: async (templateId: string, template: Partial<CreateTemplatePayload>) => {
    try {
      set({ isTemplateActionLoading: true, templateError: null });
      const response = await templateApi.updateTemplate(templateId, template);
      if (response.data) {
        const templates = get().templates;
        const updatedTemplates = templates.map(t => 
          t.template_id === templateId ? response.data : t
        );
        set({ templates: updatedTemplates });
      }
      return response.data;
    } catch (error) {
      set({ templateError: error instanceof Error ? error.message : 'An error occurred' });
      throw error;
    } finally {
      set({ isTemplateActionLoading: false });
    }
  },

  deleteTemplate: async (templateId: string) => {
    set({ isTemplateActionLoading: true, templateError: null });

    try {
      await templateApi.deleteTemplate(templateId);
      set((state) => ({
        templates: state.templates.filter(t => t.template_id !== templateId),
        currentTemplate: state.currentTemplate?.template_id === templateId ? null : state.currentTemplate
      }));
    } catch (error) {
      set({ templateError: error instanceof Error ? error.message : 'An error occurred' });
    } finally {
      set({ isTemplateActionLoading: false });
    }
  },

  fetchParameters: async () => {
    const state = get();
    
    // Always set loading state when starting to fetch
    set({ isParametersLoading: true, parametersError: null });

    try {
      // Make API call regardless of cache state to ensure fresh data
      const response = await api.get('/parameters/all');
      
      if (response.data) {
        // Update cache timestamp
        cacheManager.updateParametersFetchTimestamp();
        
        // Update state with fetched data
        set({
          parameters: response.data,
          parameterValues: response.data.reduce((acc: Record<string, any>, param: Parameter) => {
            acc[param.parameter_id] = param.values || [];
            return acc;
          }, {...state.parameterValues}),
          isParametersLoading: false,
          parametersError: null
        });
      }
    } catch (error) {
      console.error('Error fetching parameters:', error);
      set({ 
        parametersError: error instanceof Error ? error.message : 'An error occurred',
        isParametersLoading: false 
      });
    }
  },

  fetchParameterValues: async (parameterId: string) => {
    // Check if we already have values for this parameter
    const existingValues = get().parameterValues[parameterId];
    if (existingValues && existingValues.length > 0) {
      return; // We already have the values, no need to fetch
    }

    try {
      const response = await api.get(`/parameters/${parameterId}/values`);
      if (response.data) {
        set((state) => ({
          parameterValues: {
            ...state.parameterValues,
            [parameterId]: response.data
          }
        }));
      }
    } catch (error) {
      set({ parametersError: error instanceof Error ? error.message : 'An error occurred' });
    }
  },
  
  createParameter: async (parameter) => {
    try {
      const response = await api.post('/parameters', parameter);
      if (response.data) {
        // Update local state without full refetch
        set((state) => ({
          parameters: [...state.parameters, response.data],
        }));
      }
    } catch (error) {
      console.error('Error creating parameter:', error);
      throw error;
    }
  },

  updateParameter: async (parameterId, parameter) => {
    try {
      const response = await api.put(`/parameters/${parameterId}`, parameter);
      if (response.data) {
        // Update the parameter in local state
        set((state) => ({
          parameters: state.parameters.map(p => 
            p.parameter_id === parameterId ? { ...p, ...response.data } : p
          ),
        }));
      }
    } catch (error) {
      console.error('Error updating parameter:', error);
      throw error;
    }
  },

  deleteParameter: async (parameterId) => {
    try {
      await api.delete(`/parameters/${parameterId}`);
      // Update local state directly
      set((state) => ({
        parameters: state.parameters.filter(p => p.parameter_id !== parameterId),
        parameterValues: (() => {
          const newValues = {...state.parameterValues};
          delete newValues[parameterId];
          return newValues;
        })(),
      }));
    } catch (error) {
      console.error('Error deleting parameter:', error);
      throw error;
    }
  },

  createParameterValue: async (parameterId, value) => {
    try {
      const response = await api.post(`/parameters/${parameterId}/values`, value);
      if (response.data) {
        // Update local state directly
        set((state) => {
          // Find and update the parameter
          const parameterIndex = state.parameters.findIndex(p => p.parameter_id === parameterId);
          const updatedParameters = [...state.parameters];
          
          if (parameterIndex >= 0) {
            const parameter = updatedParameters[parameterIndex];
            const values = Array.isArray(parameter.values) ? parameter.values : [];
            updatedParameters[parameterIndex] = {
              ...parameter,
              values: [...values, response.data]
            };
            
            // Return updated state
            return {
              parameters: updatedParameters,
              parameterValues: {
                ...state.parameterValues,
                [parameterId]: [...(state.parameterValues[parameterId] || []), response.data]
              }
            };
          }
          return state;
        });
      }
    } catch (error) {
      console.error('Error creating parameter value:', error);
      throw error;
    }
  },

  updateParameterValue: async (parameterId, valueId, value) => {
    try {
      const response = await api.put(`/parameters/${parameterId}/values/${valueId}`, value);
      if (response.data) {
        // Update the value in local state
        set((state) => {
          // Update in parameters array
          const parameterIndex = state.parameters.findIndex(p => p.parameter_id === parameterId);
          let updatedParameters = [...state.parameters];
          
          if (parameterIndex >= 0) {
            const parameter = updatedParameters[parameterIndex];
            const updatedValues = parameter.values?.map(v => 
              v.value_id === valueId ? { ...v, ...response.data } : v
            ) || [];
            
            updatedParameters[parameterIndex] = {
              ...parameter,
              values: updatedValues
            };
          }
          
          // Also update in parameterValues map
          const currentValues = state.parameterValues[parameterId] || [];
          const updatedValues = currentValues.map(v => 
            v.value_id === valueId ? { ...v, ...response.data } : v
          );
          
          return {
            parameters: updatedParameters,
            parameterValues: {
              ...state.parameterValues,
              [parameterId]: updatedValues
            }
          };
        });
      }
    } catch (error) {
      console.error('Error updating parameter value:', error);
      throw error;
    }
  },

  deleteParameterValue: async (parameterId, valueId) => {
    try {
      await api.delete(`/parameters/${parameterId}/values/${valueId}`);
      
      // Update local state directly
      set((state) => {
        // Update in parameters array
        const parameterIndex = state.parameters.findIndex(p => p.parameter_id === parameterId);
        let updatedParameters = [...state.parameters];
        
        if (parameterIndex >= 0) {
          const parameter = updatedParameters[parameterIndex];
          const updatedValues = parameter.values?.filter(v => v.value_id !== valueId) || [];
          
          updatedParameters[parameterIndex] = {
            ...parameter,
            values: updatedValues
          };
        }
        
        // Also update in parameterValues map
        const currentValues = state.parameterValues[parameterId] || [];
        const updatedValues = currentValues.filter(v => v.value_id !== valueId);
        
        return {
          parameters: updatedParameters,
          parameterValues: {
            ...state.parameterValues,
            [parameterId]: updatedValues
          }
        };
      });
    } catch (error) {
      console.error('Error deleting parameter value:', error);
      throw error;
    }
  },

  deletePost: async (threadId: string) => {
    const { fetchPosts } = get();
    try {
      set({ isLoading: true });
      await deleteContent(threadId);
      
      // Update local state
      set(state => ({
        posts: state.posts.filter(post => post.thread_id !== threadId),
        currentPost: state.currentPost?.thread_id === threadId ? null : state.currentPost
      }));
      
      // Refresh the list
      await fetchPosts({});
      set({ isLoading: false, error: null });
    } catch (error) {
      console.error('Error deleting post:', error);
      set({ isLoading: false, error: 'Failed to delete post' });
      throw error;
    }
  },

  // Update cleanup-related functions to use cacheManager
  clearTemplateCache: () => {
    cacheManager.clearTemplateCache();
    set({ templates: [] });
  },

  clearContentCache: () => {
    cacheManager.clearContentCache();
    set({ posts: [], lastLoadedSkip: -1, hasReachedEnd: false });
  },

  clearAllCaches: () => {
    cacheManager.clearAllCaches();
    set({ 
      templates: [], 
      posts: [], 
      lastLoadedSkip: -1,
      hasReachedEnd: false,
      trendingBlogTopics: [],
    });
  },

  // Update image caching to use cacheManager
  cacheTemplateImages: async (templates: Template[]) => {
    const imageUrls = templates
      .map(template => template.template_image_url)
      .filter((url): url is string => !!url);
    
    if (imageUrls.length > 0) {
      await cacheManager.preloadImages(imageUrls);
    }
  },

  // Add cache statistics helper
  getCacheStats: () => {
    return cacheManager.getCacheStats();
  }

}));