import api from './api';

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
      // Note: Backend will verify userId matches the authenticated user
      const response = await api.get(`/profiles?user_id=${userId}`);
      return response.data?.[0] || null;
    } catch (error) {
      console.error('Get profile error:', error);
      return null;
    }
  },

  async createProfile(userId: string, profileData: CreateProfileData) {
    console.log('Creating profile for user:', userId, 'with data:', profileData);
    
    try {
      const response = await api.post('/profiles', {
        ...profileData,
        role: profileData.role || 'free',
        subscription_status: profileData.subscription_status || 'none',
        generations_used: 0,
        is_deleted: false,
        preferences: profileData.preferences || {}
      });
      
      console.log('Profile created successfully:', response.data);
      return response.data as ProfileData;
    } catch (error) {
      console.error('Profile creation error:', error);
      throw error;
    }
  },

  async updateProfile(userId: string, profileData: Partial<Omit<ProfileData, 'id' | 'user_id' | 'created_at'>>) {
    try {
      // First get the profile to get its ID
      const profile = await this.getProfile(userId);
      if (!profile) throw new Error('Profile not found');
      
      const response = await api.put(`/profiles/${profile.id}`, profileData);
      return response.data as ProfileData;
    } catch (error) {
      console.error('Update profile error:', error);
      throw error;
    }
  },

  async checkProfileExists(userId: string) {
    try {
      const profile = await this.getProfile(userId);
      return Boolean(profile);
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
      // First get the profile to get its ID
      const profile = await this.getProfile(userId);
      if (!profile) throw new Error('Profile not found');
      
      await api.delete(`/profiles/${profile.id}`);
      return true;
    } catch (error) {
      console.error('Soft delete profile error:', error);
      throw error;
    }
  }
}