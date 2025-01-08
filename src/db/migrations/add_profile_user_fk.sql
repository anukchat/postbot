-- Add foreign key constraint to profiles table
ALTER TABLE profiles
ADD CONSTRAINT fk_profiles_users
FOREIGN KEY (user_id) 
REFERENCES auth.users(id)
ON DELETE CASCADE;

-- Add unique constraint on user_id to ensure one profile per user
ALTER TABLE profiles
ADD CONSTRAINT unique_user_profile
UNIQUE (user_id);
