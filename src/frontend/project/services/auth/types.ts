/**
 * Authentication service abstraction layer.
 * 
 * Supports multiple OAuth providers (Supabase, Auth0, Clerk) with a unified interface.
 * Provider can be switched via VITE_AUTH_PROVIDER environment variable.
 */

export interface AuthUser {
  id: string;
  email: string;
  emailVerified?: boolean;
  fullName?: string;
  avatarUrl?: string;
  provider?: string;
  metadata?: any;
}

export interface AuthSession {
  accessToken: string;
  refreshToken?: string;
  tokenType?: string;
  expiresAt?: number;
  user?: AuthUser;
}

export interface AuthProvider {
  /**
   * Get the provider name
   */
  getProviderName(): string;

  /**
   * Sign in with Google OAuth
   */
  signInWithGoogle(): Promise<{ data: any; error: any }>;

  /**
   * Sign in with email and password
   */
  signInWithEmail(email: string, password: string): Promise<{ data: any; error: any }>;

  /**
   * Sign up with email and password
   */
  signUpWithEmail(email: string, password: string): Promise<{ data: any; error: any }>;

  /**
   * Sign out current user
   */
  signOut(): Promise<void>;

  /**
   * Get current session
   */
  getSession(): Promise<AuthSession | null>;

  /**
   * Send password reset email
   */
  resetPassword(email: string): Promise<void>;

  /**
   * Listen for auth state changes
   */
  onAuthStateChange(callback: (session: AuthSession | null) => void): { unsubscribe: () => void };

  /**
   * Check if user exists
   */
  checkUserExists(email: string): Promise<boolean>;
}
