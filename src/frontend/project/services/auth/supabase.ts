/**
 * Supabase authentication provider implementation.
 */
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { AuthProvider, AuthSession } from './types';

export class SupabaseAuthProvider implements AuthProvider {
  private client: SupabaseClient;
  private redirectBase: string;

  constructor(
    supabaseUrl: string,
    supabaseKey: string,
    redirectUrl?: string
  ) {
    if (!supabaseUrl || !supabaseKey) {
      throw new Error('Supabase URL and key are required');
    }

    this.client = createClient(supabaseUrl, supabaseKey, {
      auth: {
        autoRefreshToken: true,
        persistSession: true
      }
    });

    this.redirectBase = redirectUrl 
      ? redirectUrl.replace(/\/$/, '') 
      : window.location.origin;
  }

  getProviderName(): string {
    return 'supabase';
  }

  async signInWithGoogle() {
    try {
      const { data, error } = await this.client.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${this.redirectBase}/auth/callback`,
          queryParams: {
            access_type: 'offline',
          }
        }
      });

      if (error) throw error;
      return { data, error: null };
    } catch (error) {
      console.error('Google sign-in error:', error);
      return { data: null, error };
    }
  }

  async signInWithEmail(email: string, password: string) {
    try {
      const { data, error } = await this.client.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;
      return { data, error: null };
    } catch (error) {
      console.error('Email sign-in error:', error);
      return { data: null, error };
    }
  }

  async signUpWithEmail(email: string, password: string) {
    try {
      const { data, error } = await this.client.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: `${this.redirectBase}/auth/callback?noAutoSignIn=true`,
          data: {
            email,
            role: 'free',
            subscription_status: 'none'
          }
        }
      });

      if (error) throw error;

      // Sign out immediately to prevent auto-login
      await this.client.auth.signOut();

      return { data, error: null };
    } catch (error) {
      console.error('Email sign-up error:', error);
      return { data: null, error };
    }
  }

  async signOut() {
    try {
      const { error } = await this.client.auth.signOut();
      if (error) throw error;
    } catch (error) {
      console.error('Sign out error:', error);
      throw error;
    }
  }

  async getSession(): Promise<AuthSession | null> {
    try {
      const { data: { session }, error } = await this.client.auth.getSession();
      if (error) throw error;

      if (!session) return null;

      console.log('[SUPABASE] Raw session:', {
        hasAccessToken: !!session.access_token,
        accessTokenLength: session.access_token?.length,
        hasUser: !!session.user,
        userId: session.user?.id
      });

      return {
        accessToken: session.access_token,
        refreshToken: session.refresh_token,
        tokenType: session.token_type || 'bearer',
        expiresAt: session.expires_at,
        user: session.user ? {
          id: session.user.id,
          email: session.user.email || '',
          emailVerified: !!session.user.email_confirmed_at,
          fullName: session.user.user_metadata?.full_name,
          avatarUrl: session.user.user_metadata?.avatar_url,
          provider: session.user.app_metadata?.provider,
          metadata: session.user.user_metadata
        } : undefined
      };
    } catch (error) {
      console.error('Get session error:', error);
      throw error;
    }
  }

  async resetPassword(email: string) {
    try {
      const { error } = await this.client.auth.resetPasswordForEmail(email, {
        redirectTo: `${this.redirectBase}/auth/callback`,
      });
      if (error) throw error;
    } catch (error) {
      console.error('Reset password error:', error);
      throw error;
    }
  }

  onAuthStateChange(callback: (session: AuthSession | null) => void) {
    const { data: { subscription } } = this.client.auth.onAuthStateChange(
      async (_, session) => {
        if (!session) {
          callback(null);
          return;
        }

        callback({
          accessToken: session.access_token,
          refreshToken: session.refresh_token,
          tokenType: session.token_type || 'bearer',
          expiresAt: session.expires_at,
          user: {
            id: session.user.id,
            email: session.user.email || '',
            emailVerified: !!session.user.email_confirmed_at,
            fullName: session.user.user_metadata?.full_name,
            avatarUrl: session.user.user_metadata?.avatar_url,
            provider: session.user.app_metadata?.provider,
            metadata: session.user.user_metadata
          }
        });
      }
    );

    return { unsubscribe: () => subscription.unsubscribe() };
  }

  async checkUserExists(email: string): Promise<boolean> {
    // Note: This requires direct database access
    // For production, implement via backend API
    console.warn(`checkUserExists should be implemented via backend API for: ${email}`);
    return false;
  }
}
