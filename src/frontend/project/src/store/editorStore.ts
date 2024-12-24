import { create } from 'zustand';
import { Post } from '../types';
import axios from 'axios';

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
  updateContent: (content: string) => void;
  updateTwitterPost: (twitter_post: string) => void;
  updateLinkedinPost: (linkedin_post: string) => void;
  savePost: () => Promise<void>;
  publishPost: () => Promise<void>;
  rejectPost: () => Promise<void>;
  downloadMarkdown: () => void;
  prependMetadata: (content: string) => string;
  undo: () => void;
  redo: () => void;
}

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
  limit: 200,
  totalPosts: 0,
  setCurrentPost: (post) => set({ currentPost: post, history: [], future: [], isContentUpdated: false }),
  toggleTheme: () => set((state) => ({ isDarkMode: !state.isDarkMode })),
  setPosts: (posts) => set({ posts }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  fetchPosts: async (filters, skip = 0, limit = 200) => {
    set({ isLoading: true });
    try {
      const params = { ...filters, skip, limit };
      if (params.status === 'All') {
        delete params.status;
      }
      const response = await axios.get('http://localhost:8000/blogs/details', { params });
      if (response.data && Array.isArray(response.data)) {
        const formattedBlogs = response.data.map((item: any) => ({
          id: item.blog.id,
          title: item.blog.title || item.blog.content.substring(0, 20),
          content: item.blog.content,
          twitter_post: item.blog.twitter_post,
          linkedin_post: item.blog.linkedin_post,
          status: item.blog.status || 'Draft',
          blog_category: item.blog.blog_category,
          tags: item.blog.tags,
          createdAt: item.blog.created_at,
          updatedAt: item.blog.updated_at,
          tweet: item.tweet,
          urls: item.urls.map((url: any) => ({ original_url: url.original_url })),
          media: item.media.map((media: any) => ({ original_url: media.original_url, type: media.type})),
        }));
        set((state) => ({
          posts: skip === 0 ? formattedBlogs : [...state.posts, ...formattedBlogs],
          totalPosts: response.data.length,
          isLoading: false,
          error: null,
          skip,
          limit
        }));
      } else {
        set({ posts: [], totalPosts: 0, isLoading: false, error: 'Error fetching blogs' });
      }
    } catch (error) {
      console.error('Error fetching blogs:', error);
      set({ posts: [], totalPosts: 0, isLoading: false, error: 'Error fetching blogs' });
    }
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
  undo: () => {
    set((state) => {
      if (state.history.length === 0) return state;

      const previousContent = state.history[state.history.length - 1];
      const newHistory = state.history.slice(0, -1);

      return {
        ...state,
        currentPost: state.currentPost
          ? { ...state.currentPost, content: previousContent }
          : null,
        history: newHistory,
        future: [state.currentPost?.content || '', ...state.future],
        isContentUpdated: true,
      };
    });
  },
  redo: () => {
    set((state) => {
      if (state.future.length === 0) return state;

      const nextContent = state.future[0];
      const newFuture = state.future.slice(1);

      return {
        ...state,
        currentPost: state.currentPost
          ? { ...state.currentPost, content: nextContent }
          : null,
        history: [...state.history, state.currentPost?.content || ''],
        future: newFuture,
        isContentUpdated: true,
      };
    });
  },
  savePost: async () => {
    const { currentPost, fetchPosts, skip, limit } = get();
    if (!currentPost) return;

    try {
      set({ isLoading: true });
      const response = await axios.put(`http://localhost:8000/blogs/${currentPost.id}`, {
        title: currentPost.title,
        content: currentPost.content,
        status: 'Draft',
        blog_category: currentPost.blog_category,
        tags: currentPost.tags,
      });

      if (response.data) {
        set((state) => ({
          currentPost: {
            ...state.currentPost!,
            ...response.data,
          },
          isLoading: false,
          error: null,
          isContentUpdated: false,
        }));
        await fetchPosts({}, skip, limit);
      }
    } catch (error) {
      set({ isLoading: false, error: 'Failed to save post' });
      console.error('Error saving post:', error);
    }
  },

  publishPost: async () => {
    const { currentPost, fetchPosts, skip, limit } = get();
    if (!currentPost) return;

    try {
      set({ isLoading: true });
      const response = await axios.put(`http://localhost:8000/blogs/${currentPost.id}`, {
        // title: currentPost.title,
        content: currentPost.content,
        status: 'Published',
        blog_category: currentPost.blog_category,
        tags: currentPost.tags,
      });

      if (response.data) {
        set((state) => ({
          currentPost: {
            ...state.currentPost!,
            ...response.data,
          },
          isLoading: false,
          error: null,
          isContentUpdated: false,
        }));
        await fetchPosts({}, skip, limit);
      }
    } catch (error) {
      set({ isLoading: false, error: 'Failed to publish post' });
      console.error('Error publishing post:', error);
    }
  },

  rejectPost: async () => {
    const { currentPost, fetchPosts, skip, limit } = get();
    if (!currentPost) return;

    try {
      set({ isLoading: true });
      const response = await axios.put(`http://localhost:8000/blogs/${currentPost.id}`, {
        // title: currentPost.title,
        content: currentPost.content,
        status: 'Rejected',
        blog_category: currentPost.blog_category,
        tags: currentPost.tags,
      });

      if (response.data) {
        set((state) => ({
          currentPost: {
            ...state.currentPost!,
            ...response.data,
          },
          isLoading: false,
          error: null,
          isContentUpdated: false,
        }));
        await fetchPosts({}, skip, limit);
      }
    } catch (error) {
      set({ isLoading: false, error: 'Failed to reject post' });
      console.error('Error rejecting post:', error);
    }
  },

  downloadMarkdown: () => {
    const { currentPost } = get();
    if (!currentPost) return;

    const content = currentPost.content//get().prependMetadata(currentPost.content);
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
category: ${currentPost.blog_category || ''}
date: ${currentPost.createdAt}
author: Anukool Chaturvedi
tags: ${currentPost.tags.join(', ')}
language: English
excerpt: 1...
---

${content}`;
    return frontmatter;
  },
}));