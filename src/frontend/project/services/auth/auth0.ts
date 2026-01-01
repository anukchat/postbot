/**
 * Auth0 authentication provider implementation.
 * 
 * IMPORTANT: Requires @auth0/auth0-spa-js package
 * Install before using Auth0: npm install @auth0/auth0-spa-js
 * 
 * This file will show TypeScript errors until the package is installed.
 */
import { AuthProvider, AuthSession } from './types';

export class Auth0AuthProvider implements AuthProvider {
  private auth0Client: any;
  private domain: string;
  private clientId: string;
  private redirectUri: string;

  constructor(domain: string, clientId: string, redirectUri?: string) {
    if (!domain || !clientId) {
      throw new Error('Auth0 domain and clientId are required');
    }

    this.domain = domain;
    this.clientId = clientId;
    this.redirectUri = redirectUri || `${window.location.origin}/auth/callback`;

    // Lazy load Auth0 client
    this.initializeAuth0();
  }

  private async initializeAuth0() {
    try {
      const { createAuth0Client } = await import('@auth0/auth0-spa-js');
      this.auth0Client = await createAuth0Client({
        domain: this.domain,
        clientId: this.clientId,
        authorizationParams: {
          redirect_uri: this.redirectUri,
          scope: 'openid profile email'
        }
      });
    } catch (error) {
      console.error('Failed to initialize Auth0:', error);
      throw new Error('Auth0 SDK not installed. Run: npm install @auth0/auth0-spa-js');
    }
  }

  getProviderName(): string {
    return 'auth0';
  }

  async signInWithGoogle() {
    try {
      await this.auth0Client.loginWithRedirect({
        authorizationParams: {
          connection: 'google-oauth2'
        }
      });
      return { data: true, error: null };
    } catch (error) {
      console.error('Google sign-in error:', error);
      return { data: null, error };
    }
  }

  async signInWithEmail(email: string, password: string) {
    try {
      await this.auth0Client.loginWithCredentials({
        username: email,
        password: password,
        realm: 'Username-Password-Authentication'
      });
      return { data: true, error: null };
    } catch (error) {
      console.error('Email sign-in error:', error);
      return { data: null, error };
    }
  }

  async signUpWithEmail(email: string, password: string): Promise<{ data: any; error: any }> {
    // Auth0 signup typically done via backend or Universal Login
    console.warn(`Auth0 signUpWithEmail not fully implemented for: ${email}, password length: ${password.length}`);
    return {
      data: null,
      error: new Error('Auth0 signup should be handled via Universal Login or backend API')
    };
  }

  async signOut() {
    try {
      await this.auth0Client.logout({
        logoutParams: {
          returnTo: window.location.origin
        }
      });
    } catch (error) {
      console.error('Sign out error:', error);
      throw error;
    }
  }

  async getSession(): Promise<AuthSession | null> {
    try {
      const isAuthenticated = await this.auth0Client.isAuthenticated();
      if (!isAuthenticated) return null;

      const token = await this.auth0Client.getTokenSilently();
      const user = await this.auth0Client.getUser();

      return {
        accessToken: token,
        tokenType: 'bearer',
        user: user ? {
          id: user.sub || '',
          email: user.email || '',
          emailVerified: user.email_verified || false,
          fullName: user.name,
          avatarUrl: user.picture,
          provider: 'auth0',
          metadata: user
        } : undefined
      };
    } catch (error) {
      console.error('Get session error:', error);
      return null;
    }
  }

  async resetPassword(email: string): Promise<void> {
    // Auth0 password reset via backend or Management API
    console.warn(`Auth0 password reset not implemented for: ${email}`);
    throw new Error('Auth0 password reset should be handled via backend API');
  }

  onAuthStateChange(callback: (session: AuthSession | null) => void) {
    // Auth0 doesn't have built-in state change listener
    // Implement polling or use Auth0's events
    let interval: NodeJS.Timeout;

    const checkAuth = async () => {
      const session = await this.getSession();
      callback(session);
    };

    // Check every 30 seconds
    interval = setInterval(checkAuth, 30000);
    checkAuth(); // Initial check

    return {
      unsubscribe: () => clearInterval(interval)
    };
  }

  async checkUserExists(email: string): Promise<boolean> {
    // Implement via backend API
    console.warn(`checkUserExists should be implemented via backend API for: ${email}`);
    return false;
  }
}
