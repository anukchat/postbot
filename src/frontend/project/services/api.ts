import axios from 'axios';
import { authService } from './auth';
import { TemplateFilter } from '../store/editorStore';
import { supabaseClient } from '../utils/supaclient';
import Cookies from 'js-cookie';

// Use a more reliable way to determine the API URL, with a consistent path structure
const getApiBaseUrl = () => {
  const apiUrl = import.meta.env.VITE_API_URL;
  
  if (!apiUrl) {
    console.warn('VITE_API_URL is not set, using development fallback');
    if (import.meta.env.DEV) {
      return 'http://localhost:8000';
    }
    throw new Error('VITE_API_URL environment variable is required in production');
  }

  // Remove trailing slash if present
  return apiUrl.endsWith('/') ? apiUrl.slice(0, -1) : apiUrl;
};

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add request interceptor with error handling
api.interceptors.request.use(async (config) => {
  try {
    const session = await authService.getSession();
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }
    return config;
  } catch (error) {
    console.error('Error in request interceptor:', error);
    return Promise.reject(error);
  }
}, (error) => {
  console.error('Request interceptor error:', error);
  return Promise.reject(error);
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      authService.signOut().catch(console.error);
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
    const response = await fetch(`${API_BASE_URL}/content/generate/stream`, {
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
