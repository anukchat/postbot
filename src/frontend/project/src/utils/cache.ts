const CACHE_PREFIX = 'link_preview_';
const CACHE_EXPIRY = 24 * 60 * 60 * 1000; // 24 hours

export const getLinkPreviewFromCache = (url: string) => {
  const cached = localStorage.getItem(`${CACHE_PREFIX}${url}`);
  if (!cached) return null;

  const { data, timestamp } = JSON.parse(cached);
  if (Date.now() - timestamp > CACHE_EXPIRY) {
    localStorage.removeItem(`${CACHE_PREFIX}${url}`);
    return null;
  }

  return data;
};

export const setLinkPreviewInCache = (url: string, data: any) => {
  localStorage.setItem(
    `${CACHE_PREFIX}${url}`,
    JSON.stringify({
      data,
      timestamp: Date.now(),
    })
  );
};
