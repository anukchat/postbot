class CacheManager {
  private static instance: CacheManager;
  private cleanupInterval: NodeJS.Timeout | null = null;
  private readonly CLEANUP_INTERVAL = 1000 * 60 * 15; // 15 minutes

  private constructor() {
    this.startCleanupInterval();
    this.setupEventListeners();
  }

  static getInstance(): CacheManager {
    if (!CacheManager.instance) {
      CacheManager.instance = new CacheManager();
    }
    return CacheManager.instance;
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
    const cacheService = (window as any).cacheService;
    if (!cacheService) return;

    const stats = cacheService.getCacheStats();
    
    // Clear image cache if it's too large
    if (aggressive || stats.totalImageSize > 100 * 1024 * 1024) { // 100MB
      cacheService.clearImageCache();
    }

    // Check template cache expiry
    const templates = cacheService.getCachedTemplates();
    if (templates && Date.now() - templates.timestamp > cacheService.TEMPLATE_CACHE_EXPIRY) {
      cacheService.clearTemplateCache();
    }
  }

  dispose(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
  }
}

export const cacheManager = CacheManager.getInstance();