import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabaseClient = createClient(supabaseUrl, supabaseKey);

export const authService = {
  // Check if user exists
  async checkUserExists(email: string) {
    const { data } = await supabaseClient
      .from('profiles')
      .select('id')
      .eq('email', email)
      .single();
    return Boolean(data);
  },

  // Consolidated sign in method
  async signIn(provider: 'google' | 'email', options?: { 
    email?: string;
    password?: string;
  }) {
    if (provider === 'google') {
      return this.signInWithGoogle();
    }

    if (provider === 'email' && options?.email && options?.password) {
      return this.signInWithEmail(options.email, options.password);
    }

    throw new Error('Invalid sign in method');
  },

  // Sign in with email
  async signInWithEmail(email: string, password: string) {
    const { data, error } = await supabaseClient.auth.signInWithPassword({
      email,
      password,
    });
    if (error) throw error;
    return data;
  },

  // Sign in with Google
  async signInWithGoogle() {
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
    return data;
  },

  // Sign up with email
  async signUpWithEmail(email: string, password: string) {
    // First create auth user
    const { data: { user }, error: authError } = await supabaseClient.auth.signUp({
      email,
      password,
    });
    if (authError) throw authError;

    if (user) {
      // Create profile
      const { error: profileError } = await supabaseClient
        .from('profiles')
        .insert({
          user_id: user.id,
          email: user.email,
          role: 'free',
          subscription_status: 'none'
        });
      
      if (profileError) throw profileError;
    }

    return user;
  },

  async signOut() {
    const { error } = await supabaseClient.auth.signOut();
    if (error) throw error;
  },

  async getSession() {
    const { data: { session }, error } = await supabaseClient.auth.getSession();
    if (error) throw error;
    return session;
  },

  onAuthStateChange(callback: (session: any) => void) {
    return supabaseClient.auth.onAuthStateChange((_, session) => {
      callback(session);
    });
  },

  async createProfile(userId: string, profileData: any) {
    const { data, error } = await supabaseClient
      .from('profiles')
      .upsert([{
        user_id: userId,
        ...profileData
      }]);
    if (error) throw error;
    return data;
  },

  async getProfile(userId: string) {
    const { data, error } = await supabaseClient
      .from('profiles')
      .select('*')
      .eq('profile_id', userId)
      .single();
    if (error) throw error;
    return data;
  }
};
