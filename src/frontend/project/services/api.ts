import axios from 'axios';
import { authService } from './auth';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true,  // Add this line
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

export default api;
