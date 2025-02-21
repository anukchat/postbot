import { Template } from '../store/editorStore';

const TEMPLATE_CACHE_KEY = 'cached_templates';
const TEMPLATE_CATEGORIES_CACHE_KEY = 'cached_template_categories';
const TEMPLATE_CACHE_EXPIRY = 1000 * 60 * 60; // 1 hour
const IMAGE_CACHE_SIZE = 50;
const CACHE_VERSION = '1.0'; // For cache invalidation

class CacheService {
  private imageCache: Map<string, { blob: Blob; timestamp: number }>;
  private cacheVersion: string;

  constructor() {
    this.imageCache = new Map();
    this.cacheVersion = CACHE_VERSION;
    this.validateCacheVersion();
  }

  private validateCacheVersion(): void {
    const storedVersion = localStorage.getItem('cache_version');
    if (storedVersion !== this.cacheVersion) {
      // Clear all caches if version mismatch
      this.clearCache();
      localStorage.setItem('cache_version', this.cacheVersion);
    }
  }

  async cacheTemplates(templates: Template[]): Promise<void> {
    const cacheData = {
      templates,
      timestamp: Date.now(),
      version: this.cacheVersion
    };
    localStorage.setItem(TEMPLATE_CACHE_KEY, JSON.stringify(cacheData));

    // Cache categories separately for quick access
    const categories = new Set<string>();
    templates.forEach(template => {
      const category = template.parameters.find(p => p.name === 'content_type')?.value.value;
      if (category) categories.add(category);
    });
    
    localStorage.setItem(TEMPLATE_CATEGORIES_CACHE_KEY, JSON.stringify({
      categories: Array.from(categories),
      timestamp: Date.now(),
      version: this.cacheVersion
    }));
  }

  getCachedTemplates(): Template[] | null {
    const cachedData = localStorage.getItem(TEMPLATE_CACHE_KEY);
    if (!cachedData) return null;

    const { templates, timestamp, version } = JSON.parse(cachedData);
    const isExpired = Date.now() - timestamp > TEMPLATE_CACHE_EXPIRY;
    const isVersionMismatch = version !== this.cacheVersion;

    if (isExpired || isVersionMismatch) {
      localStorage.removeItem(TEMPLATE_CACHE_KEY);
      return null;
    }

    return templates;
  }

  getCachedCategories(): string[] | null {
    const cachedData = localStorage.getItem(TEMPLATE_CATEGORIES_CACHE_KEY);
    if (!cachedData) return null;

    const { categories, timestamp, version } = JSON.parse(cachedData);
    const isExpired = Date.now() - timestamp > TEMPLATE_CACHE_EXPIRY;
    const isVersionMismatch = version !== this.cacheVersion;

    if (isExpired || isVersionMismatch) {
      localStorage.removeItem(TEMPLATE_CATEGORIES_CACHE_KEY);
      return null;
    }

    return categories;
  }

  // Image caching with improved memory management
  async cacheImage(url: string, blob: Blob): Promise<void> {
    // Clean up old cached images if memory usage is high
    if (this.getEstimatedCacheSize() > 50 * 1024 * 1024) { // 50MB limit
      this.cleanupOldImages();
    }

    this.imageCache.set(url, {
      blob,
      timestamp: Date.now()
    });
  }

  private getEstimatedCacheSize(): number {
    let totalSize = 0;
    this.imageCache.forEach(({ blob }) => {
      totalSize += blob.size;
    });
    return totalSize;
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

  getCachedImage(url: string): Blob | null {
    const cached = this.imageCache.get(url);
    if (!cached) return null;
    
    cached.timestamp = Date.now();
    return cached.blob;
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

  clearCache(): void {
    localStorage.removeItem(TEMPLATE_CACHE_KEY);
    localStorage.removeItem(TEMPLATE_CATEGORIES_CACHE_KEY);
    this.imageCache.clear();
  }

  clearTemplateCache(): void {
    localStorage.removeItem(TEMPLATE_CACHE_KEY);
    localStorage.removeItem(TEMPLATE_CATEGORIES_CACHE_KEY);
  }

  clearImageCache(): void {
    this.imageCache.clear();
  }

  invalidateTemplateCache(): void {
    this.clearTemplateCache();
    this.clearImageCache();
  }

  // For debugging and monitoring
  getCacheStats(): {
    templatesCount: number;
    categoriesCount: number;
    imagesCount: number;
    totalImageSize: number;
  } {
    const templates = this.getCachedTemplates();
    const categories = this.getCachedCategories();
    
    return {
      templatesCount: templates?.length || 0,
      categoriesCount: categories?.length || 0,
      imagesCount: this.imageCache.size,
      totalImageSize: this.getEstimatedCacheSize()
    };
  }
}

export const cacheService = new CacheService();