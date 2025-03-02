import { cacheManager } from '../services/cacheManager';

export const getLinkPreviewFromCache = (url: string) => {
  return cacheManager.getLinkPreviewFromCache(url);
};

export const setLinkPreviewInCache = (url: string, data: any) => {
  cacheManager.setLinkPreviewInCache(url, data);
};
