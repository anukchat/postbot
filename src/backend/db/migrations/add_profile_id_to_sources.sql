-- Add profile_id column to sources table
ALTER TABLE sources 
ADD COLUMN profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE;

-- Create index for better query performance
CREATE INDEX idx_sources_profile_id ON sources(profile_id);

-- Update existing records to link to profiles via user_id
-- This assumes you have existing sources and want to link them to profiles
UPDATE sources s
SET profile_id = p.id
FROM profiles p
WHERE s.profile_id IS NULL;

-- Make profile_id required after migration
ALTER TABLE sources
ALTER COLUMN profile_id SET NOT NULL;
