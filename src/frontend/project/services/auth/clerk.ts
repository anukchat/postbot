/**
 * Clerk authentication provider implementation.
 * 
 * Note: Clerk requires @clerk/clerk-react package
 * Install: npm install @clerk/clerk-react
 */
import { AuthProvider, AuthSession } from './types';

export class ClerkAuthProvider implements AuthProvider {
  private publishableKey: string;

  constructor(publishableKey: string) {
    if (!publishableKey) {
      throw new Error('Clerk publishable key is required');
    }

    this.publishableKey = publishableKey;
  }

  getProviderName(): string {
    return 'clerk';
  }

  async signInWithGoogle(): Promise<{ data: any; error: any }> {
    // Clerk OAuth is handled via ClerkProvider and useSignIn hook
    return {
      data: null,
      error: new Error('Clerk authentication should be handled via ClerkProvider and hooks')
    };
  }

  async signInWithEmail(email: string, _password: string): Promise<{ data: any; error: any }> {
    console.warn(`Clerk signInWithEmail not implemented: ${email}`);
    return {
      data: null,
      error: new Error('Clerk authentication should be handled via Clerk React hooks')
    };
  }

  async signUpWithEmail(email: string, _password: string): Promise<{ data: any; error: any }> {
    console.warn(`Clerk signUpWithEmail not implemented: ${email}`);
    return {
      data: null,
      error: new Error('Clerk authentication should be handled via Clerk React hooks')
    };
  }

  async signOut() {
    throw new Error('Clerk sign out should be handled via useClerk hook');
  }

  async getSession(): Promise<AuthSession | null> {
    throw new Error('Clerk session should be accessed via useSession hook');
  }

  async resetPassword(email: string): Promise<void> {
    console.warn(`Clerk resetPassword not implemented for: ${email}`);
    throw new Error('Clerk password reset should be handled via ClerkProvider');
  }

  onAuthStateChange(callback: (session: AuthSession | null) => void): { unsubscribe: () => void } {
    // Clerk auth state should be monitored via useAuth hook
    console.warn('Clerk auth state should be monitored via useAuth hook', callback);
    return { unsubscribe: () => {} };
  }

  async checkUserExists(email: string): Promise<boolean> {
    // Implement via backend API or Clerk management API
    console.warn(`checkUserExists not implemented for Clerk: ${email}`);
    return false;
  }

  // Clerk-specific: Return publishable key for frontend initialization
  getPublishableKey(): string {
    return this.publishableKey;
  }
}
