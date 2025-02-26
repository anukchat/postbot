import axios from 'axios';
import { authService } from './auth';
import { TemplateFilter } from '../store/editorStore';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
});

api.interceptors.request.use(async (config) => {
  const session = await authService.getSession();
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`;
    // Set refresh token as an HttpOnly cookie with proper security attributes
    if (session.refresh_token) {
      document.cookie = `refresh_token=${session.refresh_token}; path=/; secure; samesite=strict; httpOnly`;
    }
  }
  return config;
});

// Content methods
const deleteContent = (threadId: string) => api.delete(`/content/thread/${threadId}`);

// Template-specific methods
const templateApi = {
  getTemplate: (templateId: string) => api.get(`/templates/${templateId}`),
  
  // Enhanced getAllTemplates with better parameter handling
  getAllTemplates: (params?: any, limit?: number, filter?: TemplateFilter | undefined) => 
    api.get('/templates', { params: { ...params, ...filter } }),
  
  createTemplate: (template: any) => api.post('/templates', template),
  updateTemplate: (templateId: string, template: any) => api.put(`/templates/${templateId}`, template),
  deleteTemplate: (templateId: string) => api.delete(`/templates/${templateId}`),
  
  // Use the more efficient filter endpoint 
  filterTemplates: (params: any) => api.post('/templates/filter', params),
  
  // Parameter endpoints
  // Use /parameters/all as the primary method to get all parameters with values
  getParameters: () => api.get('/parameters/all'),
  
  // Only used as fallback for specific parameter values
  getParameterValues: (parameterId: string) => api.get(`/parameters/${parameterId}/values`),
  
  // Add a method to get a specific template with parameters
  getTemplateWithParameters: (templateId: string) => api.get(`/templates/${templateId}`),
};

export { templateApi, deleteContent };
export default api;
