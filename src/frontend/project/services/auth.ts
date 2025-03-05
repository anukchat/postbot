import { createClient, Session } from '@supabase/supabase-js';
import { cacheManager } from './cacheManager';
import Cookies from 'js-cookie';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabaseClient = createClient(supabaseUrl, supabaseKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    storage: {
      getItem: (key) => {
        try {
          return localStorage.getItem(key);
        } catch (error) {
          console.error('Error getting auth session:', error);
          return null;
        }
      },
      setItem: (key, value) => {
        try {
          localStorage.setItem(key, value);
        } catch (error) {
          console.error('Error setting auth session:', error);
        }
      },
      removeItem: (key) => {
        try {
          localStorage.removeItem(key);
        } catch (error) {
          console.error('Error removing auth session:', error);
        }
      }
    }
  }
});

export const authService = {
  async checkUserExists(email: string) {
    try {
      const { data, error } = await supabaseClient
        .from('profiles')
        .select('id')
        .eq('email', email)
        .single();
  
      if (error && error.code !== 'PGRST116') { // PGRST116 is "not found" error
        console.error('Error checking profile existence:', error);
        return false;
      }
  
      return Boolean(data);
    } catch (error) {
      console.error('Error checking user existence:', error);
      return false;
    }
  },

  async signIn(provider: 'google' | 'email', options?: { 
    email?: string;
    password?: string;
  }) {
    try {
      let response;
      
      if (provider === 'google') {
        response = await this.signInWithGoogle();
      } else if (provider === 'email' && options?.email && options?.password) {
        response = await this.signInWithEmail(options.email, options.password);
      } else {
        throw new Error('Invalid sign in method');
      }

      if (response.error) throw response.error;
      
      // Ensure session is properly stored
      if (response.data && 'session' in response.data && response.data.session) {
        await this.persistSession(response.data.session);
      }

      // Clear any cached data from previous session
      cacheManager.clearAllCaches();

      return response;
    } catch (error) {
      console.error('Sign in error:', error);
      throw error;
    }
  },

  async signInWithEmail(email: string, password: string) {
    try {
      const { data, error } = await supabaseClient.auth.signInWithPassword({
        email,
        password,
      });
      
      if (error) throw error;
      return { data, error: null };
    } catch (error) {
      console.error('Email sign in error:', error);
      return { data: null, error };
    }
  },

  async signInWithGoogle() {
    try {
      const { data, error } = await supabaseClient.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          scopes: 'email profile',
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          }
        }
      });

      if (error) throw error;
      return { data, error: null };
    } catch (error) {
      console.error('Google sign in error:', error);
      return { data: null, error };
    }
  },

  async signUpWithEmail(email: string, password: string) {
    try {
      // Check if user exists first
      const userExists = await this.checkUserExists(email);
      if (userExists) {
        return { data: null, error: new Error('User already exists') };
      }

      // Create new user with email verification
      const { data, error: authError } = await supabaseClient.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: `${window.location.origin}/auth/callback?noAutoSignIn=true`, // Add flag to prevent auto sign in
          data: {
            email,
            role: 'free',
            subscription_status: 'none'
          }
        }
      });

      if (authError) throw authError;
      
      if (!data?.user) {
        throw new Error('User creation failed');
      }

      // Sign out immediately to prevent auto-login state
      await supabaseClient.auth.signOut();

      return { data, error: null };
    } catch (error) {
      console.error('Email sign up error:', error);
      return { data: null, error };
    }
  },

  async resetPassword(email: string) {
    try {
      const { error } = await supabaseClient.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/callback`,
      });
      if (error) throw error;
    } catch (error) {
      console.error('Reset password error:', error);
      throw error;
    }
  },

  async signOut() {
    try {
      const { error } = await supabaseClient.auth.signOut();
      if (error) throw error;
      
      // Clean up session data
      localStorage.removeItem('supabase.auth.token');
      cacheManager.clearAllCaches();
    } catch (error) {
      console.error('Sign out error:', error);
      throw error;
    }
  },

  async getSession() {
    try {
      const { data: { session }, error } = await supabaseClient.auth.getSession();
      if (error) throw error;
      return session;
    } catch (error) {
      console.error('Get session error:', error);
      throw error;
    }
  },

  onAuthStateChange(callback: (event: string, session: Session | null) => void) {
    return supabaseClient.auth.onAuthStateChange((event, session) => {
      if (!session) {
        // Clear all caches and cookies when auth state changes to signed out
        cacheManager.clearAllCaches();
      }
      callback(event, session);
    });
  },

  async createUserProfile(userId: string, profileData: any) {
    try {
      const { error } = await supabaseClient
        .from('profiles')
        .insert({
          user_id: userId,
          ...profileData,
          role: 'free',
          subscription_status: 'none'
        })
        .single();

      if (error) throw error;
      return { error: null };
    } catch (error) {
      console.error('Profile creation error:', error);
      return { error };
    }
  },

  async persistSession(session: any) {
    try {
      // Store session in localStorage
      localStorage.setItem('supabase.auth.token', JSON.stringify(session));
    } catch (error) {
      console.error('Error persisting session:', error);
      throw error;
    }
  }
};
