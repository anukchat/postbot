import { Post } from '../types/editor';
import { Template } from '../store/editorStore';

// Cache constants
const CONTENT_CACHE_EXPIRY = 24 * 1000 * 60 * 60; // 2 minutes
const TEMPLATES_CACHE_EXPIRY = 24 * 1000 * 60 * 60; // 24 hours
const TRENDING_TOPICS_CACHE_EXPIRY = 24 * 60 * 60 * 1000; // 24 hours
const PARAMETERS_CACHE_EXPIRY = 24 * 1000 * 60 * 60; // 24 hours
const MAX_CONTENT_CACHE_SIZE = 200;
const MAX_CACHE_SIZE = 250;
const LINK_PREVIEW_PREFIX = 'link_preview_';
const LINK_PREVIEW_EXPIRY = 24 * 60 * 60 * 1000; // 24 hours
const CACHE_VERSION = '1.1'; // Versioning for easier cache invalidation

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

interface ImageCacheItem {
  blob: Blob;
  timestamp: number;
  size: number;
}

interface CacheStats {
  templatesCount: number;
  contentCacheEntries: number;
  topicsCacheEntries: number;
  imagesCount: number;
  totalImageSize: number;
  cacheVersion: string;
}

class CacheManager {
  private static instance: CacheManager;
  private cleanupInterval: NodeJS.Timeout | null = null;
  private readonly CLEANUP_INTERVAL = 1000 * 60 * 15; // 15 minutes
  
  // Cache storage
  private imageCache: Map<string, ImageCacheItem>;
  private templateCache: Record<string, CachedTemplateData> = {};
  private contentCache: Record<string, CachedContentData> = {};
  private trendingTopicsCache: Record<string, TrendingTopicsData> = {};
  private cacheVersion: string;
  private lastTemplatesFetch: number = 0;
  private lastParametersFetch: number = 0;
  private totalImageCacheSize: number = 0;
  private maxImageCacheSize: number = 100 * 1024 * 1024; // 100MB limit

  private constructor() {
    this.imageCache = new Map();
    this.cacheVersion = CACHE_VERSION;
    this.startCleanupInterval();
    this.setupEventListeners();
    this.initializeCacheFromStorage();
    this.initializeMemoryLimits();
  }

  static getInstance(): CacheManager {
    if (!CacheManager.instance) {
      CacheManager.instance = new CacheManager();
    }
    return CacheManager.instance;
  }

  // Initialize from persistent storage if available
  private initializeCacheFromStorage(): void {
    try {
      // Check if the cache version matches to avoid loading incompatible data
      const storedVersion = localStorage.getItem('cache_version');
      if (storedVersion !== this.cacheVersion) {
        // Clear all caches if version mismatch
        this.clearAllCaches();
        localStorage.setItem('cache_version', this.cacheVersion);
        return;
      }

      // Recover last fetch timestamps
      const lastTemplatesFetch = localStorage.getItem('last_templates_fetch');
      if (lastTemplatesFetch) {
        this.lastTemplatesFetch = Number(lastTemplatesFetch);
      }
      
      const lastParametersFetch = localStorage.getItem('last_parameters_fetch');
      if (lastParametersFetch) {
        this.lastParametersFetch = Number(lastParametersFetch);
      }
    } catch (error) {
      console.error('Failed to initialize cache from storage:', error);
      // Proceed with empty cache on error
    }
  }

  private initializeMemoryLimits(): void {
    // Set dynamic cache limits based on device memory
    if ('deviceMemory' in navigator) {
      const memory = (navigator as any).deviceMemory; // in GB
      this.maxImageCacheSize = Math.min(memory * 20 * 1024 * 1024, 100 * 1024 * 1024);
    }
  }

  // Link preview cache methods
  getLinkPreviewFromCache(url: string): any {
    try {
      const cached = localStorage.getItem(`${LINK_PREVIEW_PREFIX}${url}`);
      if (!cached) return null;

      const { data, timestamp } = JSON.parse(cached);
      if (Date.now() - timestamp > LINK_PREVIEW_EXPIRY) {
        localStorage.removeItem(`${LINK_PREVIEW_PREFIX}${url}`);
        return null;
      }

      return data;
    } catch (error) {
      // If we encounter any parsing errors, remove the corrupted entry
      localStorage.removeItem(`${LINK_PREVIEW_PREFIX}${url}`);
      return null;
    }
  }

  setLinkPreviewInCache(url: string, data: any): void {
    try {
      localStorage.setItem(
        `${LINK_PREVIEW_PREFIX}${url}`,
        JSON.stringify({
          data,
          timestamp: Date.now(),
        })
      );
    } catch (error) {
      console.error('Failed to cache link preview:', error);
      // Try to clear some space in localStorage if it's full
      this.cleanupOldLinkPreviews();
    }
  }

  private cleanupOldLinkPreviews(): void {
    try {
      const linkPreviews: Array<{key: string, timestamp: number}> = [];
      
      // Collect all link previews with their timestamps
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key?.startsWith(LINK_PREVIEW_PREFIX)) {
          const cached = localStorage.getItem(key);
          if (cached) {
            try {
              const { timestamp } = JSON.parse(cached);
              linkPreviews.push({ key, timestamp });
            } catch (e) {
              localStorage.removeItem(key);
            }
          }
        }
      }
      
      // Sort by timestamp (oldest first) and remove oldest 25%
      if (linkPreviews.length > 10) {
        linkPreviews.sort((a, b) => a.timestamp - b.timestamp);
        const removeCount = Math.ceil(linkPreviews.length * 0.25);
        linkPreviews.slice(0, removeCount).forEach(({ key }) => {
          localStorage.removeItem(key);
        });
      }
    } catch (error) {
      console.error('Error cleaning up link previews:', error);
    }
  }

  // Content cache methods with proper key normalization
  setContentInCache(cacheKey: string, posts: Post[], totalPosts: number): void {
    // Normalize cache key to ensure consistency
    const normalizedKey = this.normalizeKey(cacheKey);
    
    // Add new entry to cache
    this.contentCache[normalizedKey] = {
      posts,
      totalPosts,
      timestamp: Date.now()
    };
    
    // Clean up cache if it gets too big
    this.pruneCache(this.contentCache, MAX_CONTENT_CACHE_SIZE);
  }

  getContentFromCache(cacheKey: string): CachedContentData | null {
    const normalizedKey = this.normalizeKey(cacheKey);
    const cachedData = this.contentCache[normalizedKey];
    if (!cachedData) return null;
    
    const now = Date.now();
    if (now - cachedData.timestamp > CONTENT_CACHE_EXPIRY) {
      delete this.contentCache[normalizedKey];
      return null;
    }
    
    return cachedData;
  }

  // Helper to normalize cache keys
  private normalizeKey(key: string): string {
    // Ensure consistent key format for all cache entries
    if (typeof key === 'object') {
      return JSON.stringify(key);
    }
    return key;
  }

  // Template cache related methods with improved error handling
  setTemplatesInCache(cacheKey: string, templates: Template[], filter?: any): void {
    try {
      const normalizedKey = this.normalizeKey(cacheKey);
      this.templateCache[normalizedKey] = {
        templates,
        timestamp: Date.now(),
        filter
      };
      
      this.lastTemplatesFetch = Date.now();
      localStorage.setItem('last_templates_fetch', String(this.lastTemplatesFetch));
      this.pruneCache(this.templateCache, MAX_CACHE_SIZE);
    } catch (error) {
      console.error('Failed to cache templates:', error);
    }
  }

  getTemplatesFromCache(cacheKey: string): CachedTemplateData | null {
    try {
      const normalizedKey = this.normalizeKey(cacheKey);
      const cachedData = this.templateCache[normalizedKey];
      if (!cachedData) return null;
      
      const now = Date.now();
      if (now - cachedData.timestamp > TEMPLATES_CACHE_EXPIRY) {
        delete this.templateCache[normalizedKey];
        return null;
      }
      
      return cachedData;
    } catch (error) {
      console.error('Error retrieving templates from cache:', error);
      return null;
    }
  }

  // Trending topics cache with proper error handling
  setTrendingTopicsInCache(cacheKey: string, topics: string[]): void {
    try {
      const normalizedKey = this.normalizeKey(cacheKey);
      this.trendingTopicsCache[normalizedKey] = {
        topics,
        timestamp: Date.now()
      };
      
      this.pruneCache(this.trendingTopicsCache, MAX_CACHE_SIZE);
    } catch (error) {
      console.error('Failed to cache trending topics:', error);
    }
  }

  getTrendingTopicsFromCache(cacheKey: string): string[] | null {
    try {
      const normalizedKey = this.normalizeKey(cacheKey);
      const cachedData = this.trendingTopicsCache[normalizedKey];
      if (!cachedData) return null;
      
      const now = Date.now();
      if (now - cachedData.timestamp > TRENDING_TOPICS_CACHE_EXPIRY) {
        delete this.trendingTopicsCache[normalizedKey];
        return null;
      }
      
      return cachedData.topics;
    } catch (error) {
      console.error('Error retrieving trending topics from cache:', error);
      return null;
    }
  }

  // Parameters cache tracking with persistence
  updateParametersFetchTimestamp(): void {
    this.lastParametersFetch = Date.now();
    try {
      localStorage.setItem('last_parameters_fetch', String(this.lastParametersFetch));
    } catch (error) {
      console.error('Failed to store parameters timestamp:', error);
    }
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

  // Image caching with improved memory management and size tracking
  async cacheImage(url: string, blob: Blob): Promise<void> {
    try {
      // Check if we already have this image
      const existingImage = this.imageCache.get(url);
      if (existingImage) {
        // Update timestamp only if it exists
        existingImage.timestamp = Date.now();
        return;
      }

      // Calculate size for tracking
      const size = blob.size;
      
      // Update total cache size
      this.totalImageCacheSize += size;

      // Clean up old cached images if memory usage is high
      if (this.totalImageCacheSize > this.maxImageCacheSize) {
        this.cleanupOldImages(false);
      }

      this.imageCache.set(url, {
        blob,
        timestamp: Date.now(),
        size
      });
    } catch (error) {
      console.error(`Failed to cache image: ${url}`, error);
    }
  }

  getCachedImage(url: string): Blob | null {
    try {
      const cached = this.imageCache.get(url);
      if (!cached) return null;
      
      cached.timestamp = Date.now(); // Update timestamp to mark as recently used
      return cached.blob;
    } catch (error) {
      console.error(`Error retrieving image from cache: ${url}`, error);
      return null;
    }
  }

  private cleanupOldImages(aggressive: boolean = false): void {
    try {
      const entries = Array.from(this.imageCache.entries())
        .sort(([, a], [, b]) => a.timestamp - b.timestamp);
      
      // Remove oldest images until we're under the threshold
      let removedSize = 0;
      const targetSize = aggressive ? 
        this.maxImageCacheSize * 0.5 : // If aggressive, reduce to 50%
        this.maxImageCacheSize * 0.75; // Otherwise reduce to 75%
      
      for (const [url, image] of entries) {
        if (this.totalImageCacheSize - removedSize <= targetSize) {
          break;
        }
        removedSize += image.size;
        this.imageCache.delete(url);
      }
      
      // Update total cache size
      this.totalImageCacheSize -= removedSize;
    } catch (error) {
      console.error('Error cleaning up image cache:', error);
      // In case of error, clear all images as safety measure
      if (aggressive) {
        this.clearImageCache();
      }
    }
  }

  async preloadImages(urls: string[]): Promise<void> {
    if (!urls || urls.length === 0) return;
    
    try {
      const uniqueUrls = [...new Set(urls)].filter(url => 
        url && typeof url === 'string' && !this.getCachedImage(url)
      );
      
      // Process in batches to avoid overwhelming the browser
      const batchSize = 5;
      for (let i = 0; i < uniqueUrls.length; i += batchSize) {
        const batch = uniqueUrls.slice(i, i + batchSize);
        await Promise.all(
          batch.map(async (url) => {
            try {
              const response = await fetch(url);
              if (!response.ok) throw new Error(`HTTP error ${response.status}`);
              const blob = await response.blob();
              await this.cacheImage(url, blob);
            } catch (error) {
              console.error(`Failed to preload image: ${url}`, error);
            }
          })
        );
      }
    } catch (error) {
      console.error('Error in preload images batch:', error);
    }
  }

  // Helper methods for cache management with improved reliability
  private getEstimatedImageCacheSize(): number {
    return this.totalImageCacheSize;
  }

  private pruneCache<T>(cache: Record<string, T & { timestamp: number }>, maxSize: number): void {
    try {
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
    } catch (error) {
      console.error('Error pruning cache:', error);
    }
  }

  private startCleanupInterval(): void {
    // Clear any existing interval first
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    
    // Set up new cleanup interval
    this.cleanupInterval = setInterval(() => {
      this.performCleanup();
    }, this.CLEANUP_INTERVAL);
  }

  private setupEventListeners(): void {
    try {
      // Clean up when tab becomes inactive
      document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
          this.performCleanup();
        }
      });

      // Clean up before unload
      window.addEventListener('beforeunload', () => {
        if (this.cleanupInterval) {
          clearInterval(this.cleanupInterval);
        }
        // Save important cache stats before unload
        localStorage.setItem('last_templates_fetch', String(this.lastTemplatesFetch));
        localStorage.setItem('last_parameters_fetch', String(this.lastParametersFetch));
        localStorage.setItem('cache_version', this.cacheVersion);
      });

      // Handle low memory conditions if memory API available
      if ('performance' in window && 'memory' in (window.performance as any)) {
        window.addEventListener('devicemotion', () => {
          const performance = window.performance as any;
          if (performance?.memory?.usedJSHeapSize > performance?.memory?.jsHeapSizeLimit * 0.8) {
            this.performCleanup(true);
          }
        });
      }
    } catch (error) {
      console.error('Error setting up cache event listeners:', error);
    }
  }

  private performCleanup(aggressive: boolean = false): void {
    try {
      // Check image cache size
      if (aggressive || this.totalImageCacheSize > this.maxImageCacheSize * 0.8) {
        this.cleanupOldImages(aggressive);
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
      this.cleanupLocalStorageItems(LINK_PREVIEW_PREFIX, LINK_PREVIEW_EXPIRY);
    } catch (error) {
      console.error('Error during cache cleanup:', error);
      // In case of catastrophic error, reset everything
      if (aggressive) {
        this.clearAllCaches();
      }
    }
  }

  // Helper to clean up localStorage items by prefix and expiry
  private cleanupLocalStorageItems(prefix: string, expiry: number): void {
    try {
      const now = Date.now();
      const keysToRemove: string[] = [];
      
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (!key || !key.startsWith(prefix)) continue;
        
        try {
          const cachedData = localStorage.getItem(key);
          if (!cachedData) continue;
          
          const { timestamp } = JSON.parse(cachedData);
          if (now - timestamp > expiry) {
            keysToRemove.push(key);
          }
        } catch (e) {
          // If we can't parse it, remove it
          keysToRemove.push(key);
        }
      }
      
      // Remove all invalid/expired items
      keysToRemove.forEach(key => {
        localStorage.removeItem(key);
      });
    } catch (error) {
      console.error('Error cleaning up localStorage:', error);
    }
  }

  // Public clearing methods with improved error handling
  clearTemplateCache(): void {
    try {
      this.templateCache = {};
      this.lastTemplatesFetch = 0;
      localStorage.setItem('last_templates_fetch', '0');
    } catch (error) {
      console.error('Error clearing template cache:', error);
    }
  }

  clearImageCache(): void {
    try {
      this.imageCache.clear();
      this.totalImageCacheSize = 0;
    } catch (error) {
      console.error('Error clearing image cache:', error);
    }
  }

  clearContentCache(): void {
    try {
      this.contentCache = {};
    } catch (error) {
      console.error('Error clearing content cache:', error);
    }
  }

  clearTrendingTopicsCache(): void {
    try {
      this.trendingTopicsCache = {};
    } catch (error) {
      console.error('Error clearing trending topics cache:', error);
    }
  }

  clearLinkPreviewCache(): void {
    try {
      // Remove link preview items from localStorage
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key?.startsWith(LINK_PREVIEW_PREFIX)) {
          localStorage.removeItem(key);
        }
      }
    } catch (error) {
      console.error('Error clearing link preview cache:', error);
    }
  }

  clearAllCaches(): void {
    try {
      this.clearTemplateCache();
      this.clearImageCache();
      this.clearContentCache();
      this.clearTrendingTopicsCache();
      this.clearLinkPreviewCache();
      localStorage.setItem('cache_version', this.cacheVersion);
    } catch (error) {
      console.error('Error clearing all caches:', error);
    }
  }

  // For debugging and monitoring
  getCacheStats(): CacheStats {
    try {
      return {
        templatesCount: Object.values(this.templateCache).reduce((acc, item) => acc + item.templates.length, 0),
        contentCacheEntries: Object.keys(this.contentCache).length,
        topicsCacheEntries: Object.keys(this.trendingTopicsCache).length,
        imagesCount: this.imageCache.size,
        totalImageSize: this.totalImageCacheSize,
        cacheVersion: this.cacheVersion
      };
    } catch (error) {
      console.error('Error generating cache stats:', error);
      return {
        templatesCount: 0,
        contentCacheEntries: 0,
        topicsCacheEntries: 0,
        imagesCount: 0,
        totalImageSize: 0,
        cacheVersion: this.cacheVersion
      };
    }
  }

  dispose(): void {
    try {
      if (this.cleanupInterval) {
        clearInterval(this.cleanupInterval);
        this.cleanupInterval = null;
      }
      
      // Save important cache stats before disposal
      localStorage.setItem('last_templates_fetch', String(this.lastTemplatesFetch));
      localStorage.setItem('last_parameters_fetch', String(this.lastParametersFetch));
    } catch (error) {
      console.error('Error during cache manager disposal:', error);
    }
  }
}

export const cacheManager = CacheManager.getInstance();