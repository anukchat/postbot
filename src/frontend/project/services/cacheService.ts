import { Template } from '../store/editorStore';
import { cacheManager } from './cacheManager';

export class CacheService {
  constructor() {
    // Version handling is now in cacheManager
  }

  async cacheTemplates(templates: Template[]): Promise<void> {
    cacheManager.setTemplatesInCache('all_templates', templates);
  }

  getCachedTemplates(): Template[] | null {
    const cached = cacheManager.getTemplatesFromCache('all_templates');
    return cached?.templates || null;
  }

  getCachedCategories(): string[] | null {
    const cached = cacheManager.getTemplatesFromCache('all_templates');
    if (!cached?.templates) return null;

    // Extract categories from templates
    const categories = new Set<string>();
    cached.templates.forEach(template => {
      const category = template.parameters.find(p => p.name === 'content_type')?.values.value;
      if (category) categories.add(category);
    });

    return Array.from(categories);
  }

  async cacheImage(url: string, blob: Blob): Promise<void> {
    await cacheManager.cacheImage(url, blob);
  }

  getCachedImage(url: string): Blob | null {
    return cacheManager.getCachedImage(url);
  }

  async preloadImages(urls: string[]): Promise<void> {
    await cacheManager.preloadImages(urls);
  }

  clearCache(): void {
    cacheManager.clearAllCaches();
  }

  clearTemplateCache(): void {
    cacheManager.clearTemplateCache();
  }

  clearImageCache(): void {
    cacheManager.clearImageCache();
  }

  invalidateTemplateCache(): void {
    cacheManager.clearTemplateCache();
    cacheManager.clearImageCache();
  }

  getCacheStats(): {
    templatesCount: number;
    categoriesCount: number;
    imagesCount: number;
    totalImageSize: number;
  } {
    const stats = cacheManager.getCacheStats();
    const categories = this.getCachedCategories();
    
    return {
      templatesCount: stats.templatesCount,
      categoriesCount: categories?.length || 0,
      imagesCount: stats.imagesCount,
      totalImageSize: stats.totalImageSize
    };
  }
}