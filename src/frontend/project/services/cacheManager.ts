import { Post } from '../types/editor';
import { Template } from '../store/editorStore';

// Cache constants
const CONTENT_CACHE_EXPIRY = 1000 * 60 * 2; // 2 minutes
const TEMPLATES_CACHE_EXPIRY = 24 * 1000 * 60 * 60; // 24 hours
const TRENDING_TOPICS_CACHE_EXPIRY = 24 * 60 * 60 * 1000; // 24 hours
const PARAMETERS_CACHE_EXPIRY = 24 * 1000 * 60 * 60; // 24 hours
const MAX_CONTENT_CACHE_SIZE = 20;
const MAX_CACHE_SIZE = 250;
const LINK_PREVIEW_PREFIX = 'link_preview_';
const LINK_PREVIEW_EXPIRY = 24 * 60 * 60 * 1000; // 24 hours

// Cache interfaces
interface CachedTemplateData {
  templates: Template[];
  timestamp: number;
  filter?: any;
}

interface CachedContentData {
  posts: Post[];
  totalPosts: number;
  timestamp: number;
}

interface TrendingTopicsData {
  topics: string[];
  timestamp: number;
}

class CacheManager {
  private static instance: CacheManager;
  private cleanupInterval: NodeJS.Timeout | null = null;
  private readonly CLEANUP_INTERVAL = 1000 * 60 * 15; // 15 minutes
  
  // Cache storage
  private imageCache: Map<string, { blob: Blob; timestamp: number }>;
  private templateCache: Record<string, CachedTemplateData> = {};
  private contentCache: Record<string, CachedContentData> = {};
  private trendingTopicsCache: Record<string, TrendingTopicsData> = {};
  private cacheVersion: string;
  private lastTemplatesFetch: number = 0;
  private lastParametersFetch: number = 0;

  private constructor() {
    this.imageCache = new Map();
    this.cacheVersion = '1.0';
    this.startCleanupInterval();
    this.setupEventListeners();
  }

  static getInstance(): CacheManager {
    if (!CacheManager.instance) {
      CacheManager.instance = new CacheManager();
    }
    return CacheManager.instance;
  }

  // Link preview cache methods
  getLinkPreviewFromCache(url: string): any {
    const cached = localStorage.getItem(`${LINK_PREVIEW_PREFIX}${url}`);
    if (!cached) return null;

    const { data, timestamp } = JSON.parse(cached);
    if (Date.now() - timestamp > LINK_PREVIEW_EXPIRY) {
      localStorage.removeItem(`${LINK_PREVIEW_PREFIX}${url}`);
      return null;
    }

    return data;
  }

  setLinkPreviewInCache(url: string, data: any): void {
    localStorage.setItem(
      `${LINK_PREVIEW_PREFIX}${url}`,
      JSON.stringify({
        data,
        timestamp: Date.now(),
      })
    );
  }

  // Content cache methods
  setContentInCache(cacheKey: string, posts: Post[], totalPosts: number): void {
    // Add new entry to cache
    this.contentCache[cacheKey] = {
      posts,
      totalPosts,
      timestamp: Date.now()
    };
    
    // Clean up cache if it gets too big
    this.pruneCache(this.contentCache, MAX_CONTENT_CACHE_SIZE);
  }

  getContentFromCache(cacheKey: string): CachedContentData | null {
    const cachedData = this.contentCache[cacheKey];
    if (!cachedData) return null;
    
    const now = Date.now();
    if (now - cachedData.timestamp > CONTENT_CACHE_EXPIRY) {
      delete this.contentCache[cacheKey];
      return null;
    }
    
    return cachedData;
  }

  // Template cache related methods for admin operations
  setTemplatesInCache(cacheKey: string, templates: Template[], filter?: any): void {
    this.templateCache[cacheKey] = {
      templates,
      timestamp: Date.now(),
      filter
    };
    
    this.lastTemplatesFetch = Date.now();
    this.pruneCache(this.templateCache, MAX_CACHE_SIZE);
  }

  getTemplatesFromCache(cacheKey: string): CachedTemplateData | null {
    const cachedData = this.templateCache[cacheKey];
    if (!cachedData) return null;
    
    const now = Date.now();
    if (now - cachedData.timestamp > TEMPLATES_CACHE_EXPIRY) {
      delete this.templateCache[cacheKey];
      return null;
    }
    
    return cachedData;
  }

  // Trending topics cache
  setTrendingTopicsInCache(cacheKey: string, topics: string[]): void {
    this.trendingTopicsCache[cacheKey] = {
      topics,
      timestamp: Date.now()
    };
    
    this.pruneCache(this.trendingTopicsCache, MAX_CACHE_SIZE);
  }

  getTrendingTopicsFromCache(cacheKey: string): string[] | null {
    const cachedData = this.trendingTopicsCache[cacheKey];
    if (!cachedData) return null;
    
    const now = Date.now();
    if (now - cachedData.timestamp > TRENDING_TOPICS_CACHE_EXPIRY) {
      delete this.trendingTopicsCache[cacheKey];
      return null;
    }
    
    return cachedData.topics;
  }

  // Parameters cache tracking
  updateParametersFetchTimestamp(): void {
    this.lastParametersFetch = Date.now();
  }

  getParametersFetchTimestamp(): number {
    return this.lastParametersFetch;
  }

  isParametersCacheValid(): boolean {
    return Date.now() - this.lastParametersFetch < PARAMETERS_CACHE_EXPIRY;
  }

  getLastTemplatesFetchTimestamp(): number {
    return this.lastTemplatesFetch;
  }

  isTemplatesCacheValid(): boolean {
    return Date.now() - this.lastTemplatesFetch < TEMPLATES_CACHE_EXPIRY;
  }

  // Image caching with improved memory management
  async cacheImage(url: string, blob: Blob): Promise<void> {
    // Clean up old cached images if memory usage is high
    if (this.getEstimatedImageCacheSize() > 50 * 1024 * 1024) { // 50MB limit
      this.cleanupOldImages();
    }

    this.imageCache.set(url, {
      blob,
      timestamp: Date.now()
    });
  }

  getCachedImage(url: string): Blob | null {
    const cached = this.imageCache.get(url);
    if (!cached) return null;
    
    cached.timestamp = Date.now(); // Update timestamp to mark as recently used
    return cached.blob;
  }

  private cleanupOldImages(): void {
    const entries = Array.from(this.imageCache.entries())
      .sort(([, a], [, b]) => a.timestamp - b.timestamp);
    
    // Remove oldest 25% of images
    const removeCount = Math.ceil(entries.length * 0.25);
    entries.slice(0, removeCount).forEach(([url]) => {
      this.imageCache.delete(url);
    });
  }

  async preloadImages(urls: string[]): Promise<void> {
    const uniqueUrls = [...new Set(urls)].filter(url => !this.getCachedImage(url));
    
    // Process in batches to avoid overwhelming the browser
    const batchSize = 5;
    for (let i = 0; i < uniqueUrls.length; i += batchSize) {
      const batch = uniqueUrls.slice(i, i + batchSize);
      await Promise.all(
        batch.map(async (url) => {
          try {
            const response = await fetch(url);
            const blob = await response.blob();
            await this.cacheImage(url, blob);
          } catch (error) {
            console.error(`Failed to preload image: ${url}`, error);
          }
        })
      );
    }
  }

  // Helper methods for cache management
  private getEstimatedImageCacheSize(): number {
    let totalSize = 0;
    this.imageCache.forEach(({ blob }) => {
      totalSize += blob.size;
    });
    return totalSize;
  }

  private pruneCache<T>(cache: Record<string, T & { timestamp: number }>, maxSize: number): void {
    const keys = Object.keys(cache);
    if (keys.length <= maxSize) return;
    
    // Sort by timestamp (oldest first) and remove oldest entries
    const sortedEntries = keys
      .map(key => ({ key, timestamp: cache[key].timestamp }))
      .sort((a, b) => a.timestamp - b.timestamp);
    
    const entriesToRemove = sortedEntries.slice(0, keys.length - maxSize);
    entriesToRemove.forEach(({ key }) => {
      delete cache[key];
    });
  }

  private startCleanupInterval(): void {
    this.cleanupInterval = setInterval(() => {
      this.performCleanup();
    }, this.CLEANUP_INTERVAL);
  }

  private setupEventListeners(): void {
    // Clean up when tab becomes inactive
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.performCleanup();
      }
    });

    // Clean up before unload if needed
    window.addEventListener('beforeunload', () => {
      if (this.cleanupInterval) {
        clearInterval(this.cleanupInterval);
      }
    });

    // Handle low memory conditions
    window.addEventListener('devicemotion', () => {
      const performance = window.performance as any;
      if (performance?.memory?.usedJSHeapSize > performance?.memory?.jsHeapSizeLimit * 0.8) {
        this.performCleanup(true);
      }
    });
  }

  private performCleanup(aggressive: boolean = false): void {
    // Check image cache size
    if (aggressive || this.getEstimatedImageCacheSize() > 100 * 1024 * 1024) { // 100MB
      this.clearImageCache();
    }

    // Clean up expired content cache entries
    const now = Date.now();
    Object.keys(this.contentCache).forEach(key => {
      if (now - this.contentCache[key].timestamp > CONTENT_CACHE_EXPIRY) {
        delete this.contentCache[key];
      }
    });

    // Clean up expired template cache entries
    Object.keys(this.templateCache).forEach(key => {
      if (now - this.templateCache[key].timestamp > TEMPLATES_CACHE_EXPIRY) {
        delete this.templateCache[key];
      }
    });

    // Clean up trending topics that have expired
    Object.keys(this.trendingTopicsCache).forEach(key => {
      if (now - this.trendingTopicsCache[key].timestamp > TRENDING_TOPICS_CACHE_EXPIRY) {
        delete this.trendingTopicsCache[key];
      }
    });

    // Clean up link previews from localStorage
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(LINK_PREVIEW_PREFIX)) {
        try {
          const cachedData = localStorage.getItem(key);
          if (cachedData) {
            const { timestamp } = JSON.parse(cachedData);
            if (now - timestamp > LINK_PREVIEW_EXPIRY) {
              localStorage.removeItem(key);
            }
          }
        } catch (e) {
          localStorage.removeItem(key);
        }
      }
    }
  }

  // Public clearing methods
  clearTemplateCache(): void {
    this.templateCache = {};
  }

  clearImageCache(): void {
    this.imageCache.clear();
  }

  clearContentCache(): void {
    this.contentCache = {};
  }

  clearTrendingTopicsCache(): void {
    this.trendingTopicsCache = {};
  }

  clearLinkPreviewCache(): void {
    // Remove link preview items from localStorage
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(LINK_PREVIEW_PREFIX)) {
        localStorage.removeItem(key);
      }
    }
  }

  clearAllCaches(): void {
    this.clearTemplateCache();
    this.clearImageCache();
    this.clearContentCache();
    this.clearTrendingTopicsCache();
    this.clearLinkPreviewCache();
  }

  // For debugging and monitoring
  getCacheStats(): {
    templatesCount: number;
    contentCacheEntries: number;
    topicsCacheEntries: number;
    imagesCount: number;
    totalImageSize: number;
  } {
    return {
      templatesCount: Object.values(this.templateCache).reduce((acc, item) => acc + item.templates.length, 0),
      contentCacheEntries: Object.keys(this.contentCache).length,
      topicsCacheEntries: Object.keys(this.trendingTopicsCache).length,
      imagesCount: this.imageCache.size,
      totalImageSize: this.getEstimatedImageCacheSize()
    };
  }

  dispose(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
  }
}

export const cacheManager = CacheManager.getInstance();