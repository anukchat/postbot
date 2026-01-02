/**
 * Authentication provider factory.
 * 
 * Creates the appropriate auth provider based on environment configuration.
 * Provider selection via VITE_AUTH_PROVIDER environment variable.
 */
import { AuthProvider } from './types';
import { SupabaseAuthProvider } from './supabase';
import { Auth0AuthProvider } from './auth0';
import { ClerkAuthProvider } from './clerk';

export class AuthProviderFactory {
  private static instance: AuthProvider | null = null;

  /**
   * Get auth provider instance (singleton)
   */
  static getProvider(): AuthProvider {
    if (!AuthProviderFactory.instance) {
      AuthProviderFactory.instance = AuthProviderFactory.createProvider();
    }
    return AuthProviderFactory.instance;
  }

  /**
   * Create auth provider based on environment configuration
   */
  private static createProvider(): AuthProvider {
    const provider = (import.meta.env.VITE_AUTH_PROVIDER || 'supabase').toLowerCase();

    console.log(`Initializing auth provider: ${provider}`);

    switch (provider) {
      case 'supabase':
        return AuthProviderFactory.createSupabaseProvider();

      case 'auth0':
        return AuthProviderFactory.createAuth0Provider();

      case 'clerk':
        return AuthProviderFactory.createClerkProvider();

      default:
        console.warn(`Unknown auth provider: ${provider}, falling back to Supabase`);
        return AuthProviderFactory.createSupabaseProvider();
    }
  }

  private static createSupabaseProvider(): SupabaseAuthProvider {
    const url = import.meta.env.VITE_SUPABASE_URL;
    const key = import.meta.env.VITE_SUPABASE_ANON_KEY;
    const redirectUrl = import.meta.env.VITE_REDIRECT_URL;

    if (!url || !key) {
      throw new Error(
        'Supabase configuration missing. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY'
      );
    }

    return new SupabaseAuthProvider(url, key, redirectUrl);
  }

  private static createAuth0Provider(): Auth0AuthProvider {
    const domain = import.meta.env.VITE_AUTH0_DOMAIN;
    const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
    const redirectUri = import.meta.env.VITE_REDIRECT_URL;

    if (!domain || !clientId) {
      throw new Error(
        'Auth0 configuration missing. Set VITE_AUTH0_DOMAIN and VITE_AUTH0_CLIENT_ID'
      );
    }

    return new Auth0AuthProvider(domain, clientId, redirectUri);
  }

  private static createClerkProvider(): ClerkAuthProvider {
    const publishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

    if (!publishableKey) {
      throw new Error(
        'Clerk configuration missing. Set VITE_CLERK_PUBLISHABLE_KEY'
      );
    }

    return new ClerkAuthProvider(publishableKey);
  }

  /**
   * Reset singleton instance (useful for testing)
   */
  static reset() {
    AuthProviderFactory.instance = null;
  }
}

/**
 * Get the configured auth provider (singleton)
 */
export const getAuthProvider = () => AuthProviderFactory.getProvider();
