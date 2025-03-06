import axios from 'axios';
import Cookies from 'js-cookie';
import { authService } from './auth';
import { TemplateFilter } from '../store/editorStore';
import { supabaseClient } from '../utils/supaclient';
import { cacheManager } from './cacheManager';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  // Remove XSRF settings as they're not needed with our token approach
  xsrfCookieName: undefined,
  xsrfHeaderName: undefined
});

// Add debug logging utility
const debugLog = (message: string, data?: any) => {
  if (import.meta.env.DEV) {
    console.log(`[Auth Debug] ${message}`, data || '');
  }
};

// Add request interceptor with better production handling
api.interceptors.request.use(async (config) => {
  debugLog('Making request to:', config.url);
  try {
    const session = await authService.getSession();
    if (session?.access_token) {
      debugLog('Adding access token to request');
      config.headers.Authorization = `Bearer ${session.access_token}`;
    } else {
      debugLog('No access token available');
    }

    // Ensure CORS headers for production domains
    const origin = window.location.origin;
    if (origin.includes('render.com') || origin.startsWith('https://')) {
      config.headers['Origin'] = origin;
    }

    return config;
  } catch (error) {
    debugLog('Request interceptor error:', error);
    return Promise.reject(error);
  }
}, (error) => {
  debugLog('Request interceptor error:', error);
  return Promise.reject(error);
});

// Update response interceptor with better production error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    debugLog('Response error:', error.response?.status);
    
    // Handle offline scenario
    if (!navigator.onLine) {
      debugLog('No internet connection');
      return Promise.reject(new Error('No internet connection'));
    }

    // Handle CORS errors specifically
    if (error.message.includes('Network Error') || error.message.includes('CORS')) {
      debugLog('CORS or Network error detected');
      return Promise.reject(new Error('Unable to connect to server. Please try again.'));
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      debugLog('Attempting token refresh');
      originalRequest._retry = true;
      
      try {
        // Check for refresh token
        const refreshToken = Cookies.get('refresh_token');
        debugLog('Refresh token present:', !!refreshToken);
        
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // Try to refresh the session
        const { data: { session } } = await supabaseClient.auth.getSession();
        debugLog('Session refresh result:', !!session);
        
        if (session?.access_token) {
          debugLog('Session refresh successful');
          // Update the authorization header
          originalRequest.headers.Authorization = `Bearer ${session.access_token}`;
          // Ensure CORS headers are present in retry
          const origin = window.location.origin;
          if (origin.includes('render.com') || origin.startsWith('https://')) {
            originalRequest.headers['Origin'] = origin;
          }
          return api(originalRequest);
        } else {
          throw new Error('Session refresh failed - no new access token');
        }
      } catch (refreshError) {
        debugLog('Session refresh failed:', refreshError);
        // Clear auth state on refresh failure
        await supabaseClient.auth.signOut();
        cacheManager.clearAllCaches();
        
        // Only redirect if not already on login page
        if (!window.location.pathname.includes('/login')) {
          debugLog('Redirecting to login page');
          window.location.href = '/login?error=session_expired';
        }
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

// Content methods
const deleteContent = (threadId: string) => api.delete(`/content/thread/${threadId}`);

// Update filterContent to correctly send filters as an object/dictionary
const filterContent = (filters: Record<string, any> = {}, skip: number = 0, limit: number = 10) => {
  // Clean the filters object by removing null, undefined, and empty string values
  const cleanedFilters = Object.entries(filters).reduce((acc, [key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      acc[key] = value;
    }
    return acc;
  }, {} as Record<string, any>);

  // Convert filters to a JSON string
  const filtersJson = JSON.stringify(cleanedFilters);

  return api.get('/content/filter', { 
    params: { 
      filters: filtersJson,
      skip,
      limit
    }
  });
};

// Add streaming generate method
const generatePostStream = async (payload: any) => {
  try {
    const session = await authService.getSession();
    const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/content/generate/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session?.access_token}`,
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify(payload),
      credentials: 'include'
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `HTTP error! status: ${response.status}`);
    }

    if (!response.body) {
      throw new Error('No response body received');
    }

    const reader = response.body.getReader();
    return reader;
  } catch (error) {
    console.error('Error in generatePostStream:', error);
    throw error;
  }
};

// Template-specific methods
const templateApi = {
  getTemplate: (templateId: string) => api.get(`/templates/${templateId}`),
  
  // Fixed unused parameter by using it or removing it
  getAllTemplates: (params?: any, filter?: TemplateFilter | undefined) => {
    // Format filter to match backend expectations
    const apiParams = { 
      ...params,
      ...(filter || {})
    };
    
    // Make sure we're properly handling template_type and is_deleted which are special cases
    if (filter?.template_type) {
      apiParams.template_type = filter.template_type;
    }
    
    // Include deleted templates flag
    if (filter?.is_deleted !== undefined) {
      apiParams.include_deleted = filter.is_deleted;
    }
    
    return api.get('/templates', { params: apiParams });
  },
  
  createTemplate: (template: any) => api.post('/templates', template),
  
  updateTemplate: (templateId: string, template: any) => api.put(`/templates/${templateId}`, template),
  
  deleteTemplate: (templateId: string) => api.delete(`/templates/${templateId}`),
  
  // Use the more efficient filter endpoint 
  filterTemplates: (params: TemplateFilter) => api.post('/templates/filter', params),
  
  // Parameter endpoints
  // Use /parameters/all as the primary method to get all parameters with values
  getParameters: () => api.get('/parameters/all'),
  
  // Only used as fallback for specific parameter values
  getParameterValues: (parameterId: string) => api.get(`/parameters/${parameterId}/values`),
  
  // Add a method to get a specific template with parameters
  getTemplateWithParameters: (templateId: string) => api.get(`/templates/${templateId}`),
};

export { templateApi, deleteContent, filterContent, generatePostStream };
export default api;
