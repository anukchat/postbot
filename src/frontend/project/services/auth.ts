import { createClient } from '@supabase/supabase-js';
import axios from 'axios';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;
// Prefer explicit redirect base from env to avoid falling back to a production origin during local dev
const redirectBase = (import.meta.env.VITE_REDIRECT_URL ? (import.meta.env.VITE_REDIRECT_URL as string).replace(/\/$/, '') : window.location.origin);

export const supabaseClient = createClient(supabaseUrl, supabaseKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true
  }
});

export const authService = {
  async checkUserExists(email: string) {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || `${window.location.protocol}//${window.location.hostname}:8000/api`;
      const session = await supabaseClient.auth.getSession();
      
      const response = await axios.get(`${apiUrl}/profiles/check`, {
        params: { email },
        headers: session?.data?.session?.access_token ? {
          'Authorization': `Bearer ${session.data.session.access_token}`
        } : {}
      });
      
      return response.data.exists;
    } catch (error: any) {
      // If 404, user doesn't exist
      if (error.response?.status === 404) {
        return false;
      }
      console.error('Error checking user existence:', error);
      return false;
    }
  },

  async signIn(provider: 'google' | 'email', options?: { 
    email?: string;
    password?: string;
  }) {
    try {
      if (provider === 'google') {
        return await this.signInWithGoogle();
      }

      if (provider === 'email' && options?.email && options?.password) {
        return await this.signInWithEmail(options.email, options.password);
      }

      throw new Error('Invalid sign in method');
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
          redirectTo: `${redirectBase}/auth/callback`,
          queryParams: {
            access_type: 'offline', // Only include if you need refresh tokens
          }
        }
      });
  
      if (error) throw error;
      return { data, error: null };
    } catch (error) {
      console.error('Google sign-in error:', error);
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
          emailRedirectTo: `${redirectBase}/auth/callback?noAutoSignIn=true`, // Add flag to prevent auto sign in
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
        redirectTo: `${redirectBase}/auth/callback`,
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

  onAuthStateChange(callback: (session: any) => void) {
    return supabaseClient.auth.onAuthStateChange((_, session) => {
      callback(session);
    });
  },

  async createUserProfile(userId: string, profileData: any) {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || `${window.location.protocol}//${window.location.hostname}:8000/api`;
      const session = await supabaseClient.auth.getSession();
      
      await axios.post(`${apiUrl}/profiles`, {
        user_id: userId,
        ...profileData,
        role: 'free',
        subscription_status: 'none'
      }, {
        headers: session?.data?.session?.access_token ? {
          'Authorization': `Bearer ${session.data.session.access_token}`,
          'Content-Type': 'application/json'
        } : {
          'Content-Type': 'application/json'
        }
      });

      return { error: null };
    } catch (error) {
      console.error('Profile creation error:', error);
      return { error };
    }
  },

};
