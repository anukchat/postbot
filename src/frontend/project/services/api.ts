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
  }
  return config;
});

// Template-specific methods
const templateApi = {
  getTemplate: (templateId: string) => api.get(`/templates/${templateId}`),
  getAllTemplates: (params?: any, limit?: number, filter?: TemplateFilter | undefined) => api.get('/templates', { params }),
  createTemplate: (template: any) => api.post('/templates', template),
  updateTemplate: (templateId: string, template: any) => api.put(`/templates/${templateId}`, template),
  deleteTemplate: (templateId: string) => api.delete(`/templates/${templateId}`),
  filterTemplates: (params: any) => api.post('/templates/filter', params),
};

export { templateApi };
export default api;
