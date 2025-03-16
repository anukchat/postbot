import { supabaseClient } from '../utils/supaclient';
import { v4 as uuidv4 } from 'uuid';

interface ProfileData {
  id: string;
  user_id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  role: string;
  subscription_status: string;
  subscription_end: string | null;
  created_at: string;
  preferences: Record<string, any> | null;
  is_deleted: boolean;
  deleted_at: string | null;
  generations_used: number;
  bio: string | null;
  website: string | null;
  company: string | null;
  updated_at: string;
}

export type CreateProfileData = Omit<Partial<ProfileData>, 'id' | 'user_id'>;

export const profileService = {
  async getProfile(userId: string) {
    try {
      const { data, error } = await supabaseClient
        .from('profiles')
        .select('*')
        .eq('user_id', userId)
        .eq('is_deleted', false)
        .single();
      
      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Get profile error:', error);
      return null;
    }
  },

  async createProfile(userId: string, profileData: CreateProfileData) {
    console.log('Creating profile for user:', userId, 'with data:', profileData);
    
    let retries = 3;
    while (retries > 0) {
      try {
        const now = new Date().toISOString();
        const { data, error } = await supabaseClient
          .from('profiles')
          .upsert({
            id: uuidv4(),
            user_id: userId,
            email: profileData.email || null,
            role: profileData.role || 'free',
            subscription_status: profileData.subscription_status || 'none',
            full_name: profileData.full_name || null,
            avatar_url: profileData.avatar_url || null,
            created_at: now,
            updated_at: now,
            is_deleted: false,
            generations_used: 0,
            preferences: profileData.preferences || {},
            subscription_end: profileData.subscription_end || null,
            bio: profileData.bio || null,
            website: profileData.website || null,
            company: profileData.company || null,
            deleted_at: null
          })
          .select()
          .single();

        if (error) {
          console.error('Profile creation error:', error);
          // If it's a foreign key violation, retry
          if (error.code === '23503') {
            if (retries === 1) {
              throw new Error('User not available in auth system after retries');
            }
            await new Promise(resolve => setTimeout(resolve, 1000));
            retries--;
            continue;
          }
          throw error;
        }
        
        console.log('Profile created successfully:', data);
        return data as ProfileData;
      } catch (error) {
        if (retries === 1) throw error;
        retries--;
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    throw new Error('Failed to create profile after all retries');
  },

  async updateProfile(userId: string, profileData: Partial<Omit<ProfileData, 'id' | 'user_id' | 'created_at'>>) {
    try {
      const { data, error } = await supabaseClient
        .from('profiles')
        .update({
          ...profileData,
          updated_at: new Date().toISOString(),
        })
        .eq('user_id', userId)
        .eq('is_deleted', false)
        .select()
        .single();

      if (error) throw error;
      return data as ProfileData;
    } catch (error) {
      console.error('Update profile error:', error);
      throw error;
    }
  },

  async checkProfileExists(userId: string) {
    try {
      const { data, error } = await supabaseClient
        .from('profiles')
        .select('id')
        .eq('user_id', userId)
        .eq('is_deleted', false)
        .single();
      
      if (error) {
        // PGRST116 means no rows found, which is expected when profile doesn't exist
        if (error.code === 'PGRST116') {
          return false;
        }
        throw error;
      }
      return Boolean(data);
    } catch (error) {
      console.error('Check profile exists error:', error);
      return false;
    }
  },

  async createOrUpdateProfile(userId: string, profileData: Partial<ProfileData>) {
    try {
      return await this.createProfile(userId, profileData);
    } catch (error: any) {
      console.error('Create/Update profile error:', error);
      throw error;
    }
  },

  async softDeleteProfile(userId: string) {
    try {
      const now = new Date().toISOString();
      const { error } = await supabaseClient
        .from('profiles')
        .update({
          is_deleted: true,
          deleted_at: now,
          updated_at: now
        })
        .eq('user_id', userId)
        .eq('is_deleted', false);

      if (error) throw error;
      return true;
    } catch (error) {
      console.error('Soft delete profile error:', error);
      throw error;
    }
  }
}