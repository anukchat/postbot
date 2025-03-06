import { createClient } from '@supabase/supabase-js';
import Cookies from 'js-cookie';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

export const supabaseClient = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
    storage: {
      getItem: (key) => {
        try {
          if (key.includes('refresh_token')) {
            return Cookies.get('refresh_token') || null;
          }
          return localStorage.getItem(key);
        } catch (error) {
          console.error('Error getting auth session:', error);
          return null;
        }
      },
      setItem: (key, value) => {
        try {
          if (key.includes('refresh_token')) {
            Cookies.set('refresh_token', value, {
              path: '/',
              secure: window.location.protocol === 'https:',
              sameSite: 'Lax',
              expires: 30
            });
          } else {
            localStorage.setItem(key, value);
          }
        } catch (error) {
          console.error('Error setting auth session:', error);
        }
      },
      removeItem: (key) => {
        try {
          if (key.includes('refresh_token')) {
            Cookies.remove('refresh_token', { path: '/' });
          } else {
            localStorage.removeItem(key);
          }
        } catch (error) {
          console.error('Error removing auth session:', error);
        }
      }
    }
  }
});