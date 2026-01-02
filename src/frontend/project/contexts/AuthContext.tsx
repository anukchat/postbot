import React, { createContext, useContext, useEffect, useState } from 'react';
import { Session, User } from '@supabase/supabase-js';
import { authService } from '../services/auth';
import { profileService } from '../services/profiles';

export interface UserProfile {
  id: string;
  user_id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  role: string;
  subscription_status: string;
  generations_used: number;
}

export interface AuthContextType {
  session: Session | null;
  user: User | null;
  profile: UserProfile | null;
  signIn: (provider: 'google' | 'email', options?: { 
    email?: string;
    password?: string;
  }) => Promise<any>;
  signUp: (email: string, password: string) => Promise<any>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  checkRegistration: (email: string) => Promise<boolean>;
  checkGoogleRegistration: (user: User) => Promise<boolean>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const initializeAuth = async () => {
      try {
        // Get initial session
        const initialSession = await authService.getSession();
        
        if (mounted) {
          setSession(initialSession);
          setUser(initialSession?.user ?? null);
          
          // Fetch profile if user exists
          if (initialSession?.user) {
            try {
              const userProfile = await profileService.getProfile(initialSession.user.id);
              if (userProfile && mounted) {
                setProfile(userProfile);
              }
            } catch (error) {
              console.error('Error fetching profile:', error);
            }
          }
          
          setLoading(false);
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        setLoading(false);
      }
    };

    // Subscribe to auth state changes
    const { data: { subscription } } = authService.onAuthStateChange(async (session) => {
      if (mounted) {
        setSession(session);
        setUser(session?.user ?? null);
        
        // Fetch profile when auth state changes
        if (session?.user) {
          try {
            const userProfile = await profileService.getProfile(session.user.id);
            if (userProfile && mounted) {
              setProfile(userProfile);
            }
          } catch (error) {
            console.error('Error fetching profile on auth change:', error);
          }
        } else {
          setProfile(null);
        }
        
        setLoading(false);
      }
    });

    initializeAuth();

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []);

  const signUp = async (email: string, password: string) => {
    try {
      const { data, error } = await authService.signUpWithEmail(email, password);
      if (error) throw error;

      // For email sign up, profile will be created after email verification
      // when they first sign in
      return { data, error: null };
    } catch (error) {
      console.error('Error signing up:', error);
      throw error;
    }
  };

  const signIn = async (provider: 'google' | 'email', options?: { 
    email?: string;
    password?: string;
  }) => {
    try {
      console.log(`Attempting sign in with ${provider}`);
      const { data, error } = await authService.signIn(provider, options);
      if (error) throw error;
      if (!data) throw new Error('No data returned from sign in');

      // For Google sign in, data will have provider and url
      if ('provider' in data) {
        // For Google auth, we'll handle profile creation in the callback
        // since we need to wait for the OAuth redirect
        return { data, error: null };
      }

      // For email sign in, data will have user and session
      if ('user' in data && data.user) {
        console.log('User signed in:', data.user.id);
        
        if (provider === 'email') {
          const exists = await profileService.checkProfileExists(data.user.id);
          console.log('Profile exists check:', exists);
  setProfile(null);
  
          if (!exists) {
            console.log('Creating new profile for email user');
            await profileService.createProfile(data.user.id, {
              email: data.user.email || '',
              full_name: data.user.user_metadata?.name || null,
              avatar_url: data.user.user_metadata?.avatar_url || null,
              role: 'free',
              subscription_status: 'none',
              generations_used: 0,
              preferences: {},
              is_deleted: false
            });
          }
        }
      }

      return { data, error: null };
    } catch (error) {
      console.error('Error during sign in flow:', error);
      throw error;
    }
  };

  const signOut = async () => {
    await authService.signOut();
    setUser(null);
    setSession(null);
  };

  const checkRegistration = async (user: any) => {
    try {
      return await profileService.checkProfileExists(user.id);
    } catch (error) {
      console.error('Error checking registration:', error);
      return false;
    }
  };

  const checkGoogleRegistration = async (user: User) => {
    try {
      console.log('Checking Google registration for user:', user.id);
      const exists = await profileService.checkProfileExists(user.id);
      console.log('Profile exists:', exists);
      return exists;
    } catch (error) {
      console.error('Error checking Google registration:', error);
      return false;
    }
  };

  const resetPassword = async (email: string) => {
    try {
      await authService.resetPassword(email);
    } catch (error) {
      console.error('Error resetting password:', error);
      throw error;
    }
  };

  const value = {
    session,
    user,
    profile,
    signIn,
    signUp,
    signOut,
    resetPassword,
    checkRegistration,
    checkGoogleRegistration,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};