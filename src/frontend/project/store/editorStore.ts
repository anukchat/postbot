import { create } from 'zustand';
import { Post } from '../types';
import api from '../services/api';

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
  lastLoadedSkip: number;
  hasReachedEnd: boolean;
  fetchContentByThreadId: (thread_id: string, post_type?: string) => Promise<void>;
  generatePost: (post_types: string[], thread_id: string, payload?: GeneratePayload) => Promise<void>;
  currentTab: 'blog' | 'twitter' | 'linkedin';
  setCurrentTab: (tab: 'blog' | 'twitter' | 'linkedin') => void;
  lastRefreshTimestamp: number;
  trendingBlogTopics: string[];
  lastBlogTopicsFetch: Record<string, number>; // Changed to store per-subreddit timestamps
  trendingTopicsCache: Record<string, string[]>; // Added for subreddit caching
  fetchTrendingBlogTopics: (subreddits?: string[], limit?: number) => Promise<void>;
}

interface GeneratePayload {
  thread_id?: string;
  post_types: string[];
  feedback?: string;
  tweet_id?: string;
  url?: string;
}

const MAX_CACHE_SIZE = 250; // Maximum number of subreddits to cache

export const useEditorStore = create<EditorState>((set, get) => ({
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
  setCurrentTab: (tab) => set({ currentTab: tab }),
  setCurrentPost: (post) => {
    const { currentTab, fetchContentByThreadId } = get();
    set({ currentPost: post, history: [], future: [], isContentUpdated: false });
    
    // If we're on a social tab and selecting a new post, fetch its content
    if (post && currentTab !== 'blog') {
      const postTypeMap = {
        twitter: 'twitter',
        linkedin: 'linkedin',
        blog: 'blog'
      };
      fetchContentByThreadId(post.thread_id, postTypeMap[currentTab]);
    }
  },
  toggleTheme: () => set((state) => ({ isDarkMode: !state.isDarkMode })),
  setPosts: (posts) => set({ posts }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  lastLoadedSkip: -1,
  hasReachedEnd: false,
  lastRefreshTimestamp: Date.now(),
  
  fetchPosts: async (filters, skip = 0, limit = 20) => {
    const { isLoading, posts, hasReachedEnd } = get();
    
    // If reset flag is present, clear the existing posts
    if (filters.reset) {
      set({ 
        posts: [],
        skip: 0,
        hasReachedEnd: false,
        lastLoadedSkip: -1
      });
    }
    
    if (isLoading || (hasReachedEnd && !filters.reset)) {
      return;
    }

    set({ isLoading: true });
    try {
      // Clean up filters before sending
      const cleanedFilters = Object.entries(filters).reduce((acc, [key, value]) => {
        // Skip empty date fields
        if ((['created_after', 'created_before', 'updated_after', 'updated_before'].includes(key)) && !value) {
          return acc;
        }
        // Skip empty string fields
        if (value === '') {
          return acc;
        }
        // Format dates to ISO string if they are date fields
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
      console.log('API Response:', response.data); // Add logging
      
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

        console.log('Formatted blogs:', formattedBlogs); // Add logging

        const isLastPage = formattedBlogs.length < limit;
        const currentTotal = Math.max(
          posts.length + formattedBlogs.length,
          skip + formattedBlogs.length
        );

        set((state) => {
          const postsMap = new Map<string, Post>(
            skip === 0 
              ? formattedBlogs.map((post: Post) => [post.id, post as Post])
              : [...state.posts, ...formattedBlogs].map(post => [post.id, post as Post])
          );

          const sortedPosts = Array.from(postsMap.values())
            .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());

          return {
            posts: sortedPosts,
            totalPosts: isLastPage ? currentTotal : currentTotal + limit,
            skip: skip + formattedBlogs.length,
            lastLoadedSkip: skip,
            hasReachedEnd: isLastPage,
            limit,
            isLoading: false,
            error: null,
          };
        });
      }
    } catch (error: any) {
      console.error('Error fetching blogs:', error);
      set({ isLoading: false, error: 'Error fetching blogs' });
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
            await fetchPosts({}); // Refresh the list
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
            await fetchPosts({}); // Refresh the list
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
      // Map the post type to the correct API format
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
        // Refresh content after generation
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

  trendingBlogTopics: [],
  lastBlogTopicsFetch: {},
  trendingTopicsCache: {},

  fetchTrendingBlogTopics: async (subreddits?: string[], limit: number = 15) => {
    try {
      const now = Date.now();
      const cacheKey = subreddits ? subreddits.join(',') : 'all';
      const lastFetch = get().lastBlogTopicsFetch[cacheKey];
      const cachedTopics = get().trendingTopicsCache[cacheKey];
      
      // Clean up cache if it gets too large
      const cacheSize = Object.keys(get().trendingTopicsCache).length;
      if (cacheSize > MAX_CACHE_SIZE) {
        // Remove oldest entries based on lastFetch timestamps
        const lastFetchEntries = Object.entries(get().lastBlogTopicsFetch);
        const oldestEntries = lastFetchEntries
          .sort(([, a], [, b]) => a - b)
          .slice(0, cacheSize - MAX_CACHE_SIZE + 1)
          .map(([key]) => key);

        set(state => ({
          trendingTopicsCache: Object.fromEntries(
            Object.entries(state.trendingTopicsCache).filter(([key]) => !oldestEntries.includes(key))
          ),
          lastBlogTopicsFetch: Object.fromEntries(
            Object.entries(state.lastBlogTopicsFetch).filter(([key]) => !oldestEntries.includes(key))
          )
        }));
      }

      // Use cached data if less than 24 hours old
      if (lastFetch && cachedTopics && now - lastFetch < 24 * 60 * 60 * 1000) {
        set({ trendingBlogTopics: cachedTopics });
        return;
      }

      const params: Record<string, any> = { limit };
      if (subreddits && subreddits.length > 0) {
        params.subreddits = subreddits.join(',');
      }

      const response = await api.get('/reddit/topic-suggestions', { params });
      if (response.data?.blog_topics) {
        set((state) => ({
          trendingBlogTopics: response.data.blog_topics,
          trendingTopicsCache: {
            ...state.trendingTopicsCache,
            [cacheKey]: response.data.blog_topics
          },
          lastBlogTopicsFetch: {
            ...state.lastBlogTopicsFetch,
            [cacheKey]: now
          }
        }));
      }
    } catch (error) {
      console.error('Error fetching trending blog topics:', error);
    }
  },
}));