import { create } from 'zustand';
import { templateApi } from '../services/api';
import { Post } from '../types/editor';
import api from '../services/api';
import { cacheService } from '../services/cacheService';
import { toast } from 'react-hot-toast';

// import {
//   Template,
//   CreateTemplatePayload,
//   TemplateFilter,
//   getTemplate,
//   getTemplates,
//   createTemplate as createTemplateApi,
//   updateTemplate as updateTemplateApi,
//   deleteTemplate as deleteTemplateApi,
// } from '../services/api';

export interface TemplateParameterValue {
  parameter_id: string;
  value_id: string;
  value: string;
}

export interface TemplateParameter {
  parameter_id: string;
  name: string;
  display_name: string;
  value: TemplateParameterValue;
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
  is_deleted: boolean;
}

export interface CreateTemplatePayload {
  name: string;
  description?: string;
  template_type: string;
  template_image_url?: string;
  parameters: TemplateParameter[];
}

export interface TemplateFilter {
  persona?: string;
  age_group?: string;
  platform?: string;
  sentiment?: string;
  content_type?: string;
  template_type?: string;
  is_deleted?: boolean;
}

export interface Parameter {
  parameter_id: string;
  name: string;
  display_name: string;
  description?: string;
  is_required: boolean;
  created_at: string;
}

export interface ParameterValue {
  parameter_id: string;
  value_id: string;
  value: string;
  display_order: number;
  created_at: string;
}

export interface CachedTemplateData {
  templates: Template[];
  timestamp: number;
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
  lastBlogTopicsFetch: Record<string, number>;
  trendingTopicsCache: Record<string, { topics: string[], timestamp: number }>;
  isListLoading: boolean;
  currentTab: 'blog' | 'twitter' | 'linkedin';
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
  generatePost: (post_types: string[], thread_id: string, payload?: GeneratePayload) => Promise<void>;
  fetchTrendingBlogTopics: (subreddits?: string[], limit?: number) => Promise<void>;
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

const MAX_CACHE_SIZE = 250;

export const useEditorStore = create<CombinedState>((set, get) => ({
  // Editor State Implementation
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
  lastBlogTopicsFetch: {},
  trendingTopicsCache: {},

  // Admin State Implementation
  templates: [],
  currentTemplate: null,
  isTemplateLoading: false,
  parameters: [],
  parameterValues: {},
  isParametersLoading: false,
  parametersError: null,
  isAdminView: false,
  isTemplateActionLoading: false,
  templateError: null,

  // Editor Actions
  setCurrentTab: (tab) => set({ currentTab: tab }),
  setCurrentPost: (post) => {
    const { currentTab, fetchContentByThreadId } = get();
    set({ currentPost: post, history: [], future: [], isContentUpdated: false });
    
    if (post && currentTab !== 'blog') {
      fetchContentByThreadId(post.thread_id, currentTab);
    }
  },
  toggleTheme: () => set((state) => ({ isDarkMode: !state.isDarkMode })),
  setPosts: (posts) => set({ posts }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),

  fetchPosts: async (filters, skip = 0, limit = 20) => {
    console.log('fetchPosts called', { filters, skip, limit });
    const { isLoading, posts, hasReachedEnd, currentPost } = get();
    
    if (isLoading || (!filters.reset && hasReachedEnd)) {
      console.log('Skip fetch - loading or reached end:', { isLoading, hasReachedEnd });
      return;
    }

    // Set list loading instead of general loading
    set({ isListLoading: true });

    try {
      const cleanedFilters = Object.entries(filters).reduce((acc, [key, value]) => {
        if ((['created_after', 'created_before', 'updated_after', 'updated_before'].includes(key)) && !value) {
          return acc;
        }
        if (value === '') {
          return acc;
        }
        if (['created_after', 'created_before', 'updated_after', 'updated_before'].includes(key) && value && (typeof value === 'string' || value instanceof Date)) {
          acc[key] = new Date(value).toISOString();
          return acc;
        }
        acc[key] = value;
        return acc;
      }, {} as Record<string, any>);

      const params: Record<string, any> = { ...cleanedFilters, skip, limit, timestamp: Date.now() };
      if (params.status === 'All') {
        delete params.status;
      }
      
      const response = await api.get('/content/filter', { params });
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

        const isLastPage = formattedBlogs.length < limit;
        const currentTotal = Math.max(
          posts.length + formattedBlogs.length,
          skip + formattedBlogs.length
        );

        set((state) => {
          const existingPosts = skip === 0 ? [] : state.posts;
          const mergedPosts = [...existingPosts, ...formattedBlogs];
          
          // Create a map for quick lookups
          const postsMap = new Map(mergedPosts.map(post => [post.id, post]));
          
          // Preserve current post data if it exists
          if (currentPost) {
            // Only update non-content related fields from new data
            const newPostData = postsMap.get(currentPost.id);
            if (newPostData) {
              postsMap.set(currentPost.id, {
                ...newPostData,
                content: currentPost.content,
                twitter_post: currentPost.twitter_post,
                linkedin_post: currentPost.linkedin_post
              });
            } else {
              postsMap.set(currentPost.id, currentPost);
            }
          }

          const sortedPosts = Array.from(postsMap.values())
            .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());

          return {
            posts: sortedPosts,
            totalPosts: isLastPage ? currentTotal : currentTotal + limit,
            skip: skip + formattedBlogs.length,
            lastLoadedSkip: skip,
            hasReachedEnd: isLastPage,
            limit,
            isListLoading: false,  // Update list loading
            isLoading: false,
            error: null,
          };
        });

        return formattedBlogs;
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

  generatePost: async (post_types: string[], thread_id: string, payload?: GeneratePayload) => {
    const { currentPost, fetchContentByThreadId } = get();
    if (!currentPost) return;

    set({ isLoading: true });
    try {
      let payloadData: any = { 
        post_types: post_types.map(type => type === 'twitter' ? 'twitter' : type === 'linkedin' ? 'linkedin' : type),
        thread_id,
        ...payload
      };

      if (currentPost.source_type === 'twitter') {
        payloadData.tweet_id = currentPost.source_identifier;
      } else if (currentPost.source_type === 'web_url') {
        payloadData.url = currentPost.source_identifier;
      }

      const response = await api.post('/content/generate', payloadData);
      if (response.status !== 200) {
        throw new Error(`Generation failed: ${response.statusText}`);
      }
      if (response.data) {
        await fetchContentByThreadId(thread_id, post_types[0]);
        set({ isLoading: false, error: null });
      }
    } catch (error: any) {
      console.error('Error generating post:', error);
      if (
        error.response?.status === 403 &&
        error.response?.data?.detail?.includes("Generation limit reached")
      ) {
        throw error;
      }
      set({ isLoading: false, error: 'Error generating post' });
    }
  },

  fetchTrendingBlogTopics: async (subreddits?: string[], limit: number = 15) => {
    try {
      // Clear topics immediately
      set({ trendingBlogTopics: [] });

      const now = Date.now();
      const cacheKey = subreddits ? subreddits.join(',') : 'all';
      const cachedData = get().trendingTopicsCache[cacheKey];
      
      if (cachedData && now - cachedData.timestamp < 24 * 60 * 60 * 1000) {
        // Use cached data after clearing
        set({ 
          trendingBlogTopics: cachedData.topics,
          lastBlogTopicsFetch: {
            ...get().lastBlogTopicsFetch,
            [cacheKey]: cachedData.timestamp
          }
        });
        return;
      }

      const params: Record<string, any> = { limit };
      if (subreddits && subreddits.length > 0) {
        params.subreddits = subreddits.join(',');
      }

      const response = await api.get('/reddit/topic-suggestions', { params });
      if (response.data?.blog_topics) {
        set((state) => {
          const newCache = {
            ...state.trendingTopicsCache,
            [cacheKey]: {
              topics: response.data.blog_topics,
              timestamp: now
            }
          };

          // Clean up cache if too large
          if (Object.keys(newCache).length > MAX_CACHE_SIZE) {
            const oldestEntries = Object.entries(newCache)
              .sort(([, a], [, b]) => a.timestamp - b.timestamp)
              .slice(0, Object.keys(newCache).length - MAX_CACHE_SIZE);

            oldestEntries.forEach(([key]) => {
              delete newCache[key];
            });
          }

          return {
            trendingBlogTopics: response.data.blog_topics,
            trendingTopicsCache: newCache,
            lastBlogTopicsFetch: {
              ...state.lastBlogTopicsFetch,
              [cacheKey]: now
            }
          };
        });
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
    const { lastRefreshTimestamp, templates } = get();
    const CACHE_TIME = 5 * 60 * 1000;

    if (!forceRefresh && Date.now() - lastRefreshTimestamp < CACHE_TIME && templates.length > 0) {
      return;
    }

    set({ isTemplateLoading: true, templateError: null });

    try {
      const response = await api.get('/templates', { 
        params: { skip, limit, ...filter } 
      });
      const templates = response.data;
      set({ templates, lastRefreshTimestamp: Date.now() });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred';
      set({ templateError: errorMessage });
    } finally {
      set({ isTemplateLoading: false });
    }
  },

  createTemplate: async (template: CreateTemplatePayload) => {
    set({ isTemplateActionLoading: true, templateError: null });

    try {
      const response = await api.post('/templates', template);
      const newTemplate: Template = response.data;
      
      set((state) => ({ 
        ...state,
        templates: [newTemplate, ...state.templates],
        currentTemplate: newTemplate
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred';
      set({ templateError: errorMessage });
    } finally {
      set({ isTemplateActionLoading: false });
    }
  },

  updateTemplate: async (templateId: string, template: Partial<CreateTemplatePayload>) => {
    set({ isTemplateActionLoading: true, templateError: null });

    try {
      const response = await templateApi.updateTemplate(templateId, template);
      const updatedTemplate: Template = response.data;
      
      set((state) => ({
        ...state,
        templates: state.templates.map(t => 
          t.template_id === templateId ? updatedTemplate : t
        ),
        currentTemplate: updatedTemplate
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred';
      set({ templateError: errorMessage });
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
    set({ isParametersLoading: true, parametersError: null });
    try {
      const response = await api.get('/parameters/all');
      if (response.data) {
        const params = response.data.map((p: { parameter_id: any; name: any; display_name: any; description: any; is_required: any; created_at: any; }) => ({
          parameter_id: p.parameter_id,
          name: p.name,
          display_name: p.display_name,
          description: p.description,
          is_required: p.is_required,
          created_at: p.created_at
        }));
        
        const valuesMap: Record<string, ParameterValue[]> = {};
        response.data.forEach((p: { parameter_id: string | number; values: never[]; }) => {
          valuesMap[p.parameter_id] = p.values || [];
        });
        
        set({ 
          parameters: params, 
          parameterValues: valuesMap,
          isParametersLoading: false 
        });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch parameters';
      set({ 
        parametersError: errorMessage,
        isParametersLoading: false 
      });
      throw error;
    }
  },

  fetchParameterValues: async (parameterId: string) => {
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
      console.error('Error fetching parameter values:', error);
      throw error;
    }
  },

  createParameter: async (parameter) => {
    try {
      const response = await api.post('/parameters', parameter);
      if (response.data) {
        const { fetchParameters } = get();
        await fetchParameters();
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
        const { fetchParameters } = get();
        await fetchParameters();
      }
    } catch (error) {
      console.error('Error updating parameter:', error);
      throw error;
    }
  },

  deleteParameter: async (parameterId) => {
    try {
      await api.delete(`/parameters/${parameterId}`);
      const { fetchParameters } = get();
      await fetchParameters();
    } catch (error) {
      console.error('Error deleting parameter:', error);
      throw error;
    }
  },

  createParameterValue: async (parameterId, value) => {
    try {
      const response = await api.post(`/parameters/${parameterId}/values`, value);
      if (response.data) {
        const { fetchParameterValues } = get();
        await fetchParameterValues(parameterId);
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
        const { fetchParameterValues } = get();
        await fetchParameterValues(parameterId);
      }
    } catch (error) {
      console.error('Error updating parameter value:', error);
      throw error;
    }
  },

  deleteParameterValue: async (parameterId, valueId) => {
    try {
      await api.delete(`/parameters/${parameterId}/values/${valueId}`);
      const { fetchParameterValues } = get();
      await fetchParameterValues(parameterId);
    } catch (error) {
      console.error('Error deleting parameter value:', error);
      throw error;
    }
  },

}));