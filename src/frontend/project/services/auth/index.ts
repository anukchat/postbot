/**
 * Authentication service abstraction - Main export.
 * 
 * Usage:
 * ```typescript
 * import { authService } from './services/auth';
 * 
 * // Sign in with Google (works with Supabase/Auth0/Clerk)
 * await authService.signInWithGoogle();
 * 
 * // Get current session
 * const session = await authService.getSession();
 * ```
 */
export * from './types';
export * from './factory';
export { SupabaseAuthProvider } from './supabase';
export { Auth0AuthProvider } from './auth0';
export { ClerkAuthProvider } from './clerk';

import { getAuthProvider } from './factory';

/**
 * Unified auth service - automatically uses configured provider
 */
export const authService = getAuthProvider();

/**
 * Legacy export for backward compatibility
 * @deprecated Use `authService` instead
 */
export { authService as default };
