import React, { createContext, useContext, useEffect, useState } from 'react';
import { Session, User } from '@supabase/supabase-js';
import { supabaseClient } from '../utils/supaclient';
import { authService } from '../services/auth';

interface AuthContextType {
  session: Session | null;
  user: User | null;
  signIn: (provider: 'google' | 'email', options?: { 
    email?: string;
    password?: string;
  }) => Promise<any>;  // Removed 'magic-link' from provider type
  signUp: (email: string, password: string) => Promise<User | null>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  isRegistered: boolean;
  checkRegistration: (email: string) => Promise<boolean>;
  checkGoogleRegistration: (user: User) => Promise<boolean>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRegistered, setIsRegistered] = useState<boolean>(false);

  useEffect(() => {
    // Check for existing session in local storage first
    const checkSession = async () => {
      try {
        setLoading(true);
        // Get session from Supabase
        const { data: { session } } = await supabaseClient.auth.getSession();
        
        if (session) {
          setSession(session);
          setUser(session.user);
          // Store session in localStorage
          localStorage.setItem('session', JSON.stringify(session));
        } else {
          // Try to get session from localStorage
          const storedSession = localStorage.getItem('session');
          if (storedSession) {
            const parsedSession = JSON.parse(storedSession);
            setSession(parsedSession);
            setUser(parsedSession.user);
          }
        }
      } catch (error) {
        console.error('Session check error:', error);
      } finally {
        setLoading(false);
      }
    };

    checkSession();

    // Listen for auth changes
    const { data: { subscription } } = supabaseClient.auth.onAuthStateChange(async (event, session) => {
      if (session) {
        setSession(session);
        setUser(session.user);
        localStorage.setItem('session', JSON.stringify(session));
      } else {
        setSession(null);
        setUser(null);
        localStorage.removeItem('session');
      }
      setLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const checkRegistration = async (email: string) => {
    try {
      const { data, error } = await supabaseClient
        .from('profiles')
        .select('id')
        .eq('email', email)
        .single();
      
      const registered = Boolean(data);
      setIsRegistered(registered);
      return registered;
    } catch (error) {
      console.error('Error checking registration:', error);
      return false;
    }
  };

  const checkGoogleRegistration = async (user: User) => {
    try {
      const { data, error } = await supabaseClient
        .from('profiles')
        .select('id')
        .eq('user_id', user.id)
        .single();
      
      return Boolean(data);
    } catch (error) {
      console.error('Error checking registration:', error);
      return false;
    }
  };

  const signIn = async (provider: 'google' | 'email', options?: { 
    email?: string;
    password?: string;
  }) => {
    try {
      if (provider === 'google') {
        return await authService.signInWithGoogle();
      }
      
      if (provider === 'email' && options?.email && options?.password) {
        return await authService.signInWithEmail(options.email, options.password);
      }
    } catch (error) {
      console.error('SignIn error:', error);
      throw error;
    }
  };

  const signUp = async (email: string, password: string) => {
    try {
      // Check if user already exists
      const exists = await authService.checkUserExists(email);
      if (exists) {
        throw new Error('USER_EXISTS');
      }

      return await authService.signUpWithEmail(email, password);
    } catch (error) {
      console.error('Error signing up:', error);
      throw error;
    }
  };

  const resetPassword = async (email: string) => {
    try {
      const { error } = await supabaseClient.auth.resetPasswordForEmail(email, {
        redirectTo: import.meta.env.VITE_REDIRECT_URL,
      });
      if (error) throw error;
    } catch (error) {
      console.error('Error resetting password:', error);
      throw error;
    }
  };

  const signOut = async () => {
    try {
      const { error } = await supabaseClient.auth.signOut();
      if (error) throw error;
    } catch (error) {
      console.error('Error signing out:', error);
      throw error;
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <AuthContext.Provider value={{ 
      session, 
      user, 
      signIn, 
      signUp, 
      signOut,
      resetPassword,
      isRegistered,
      checkRegistration,
      checkGoogleRegistration,
      loading
    }}>
      {!loading && children}
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