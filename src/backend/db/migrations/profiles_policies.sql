-- Enable row level security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Allow initial profile creation" ON profiles;
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Users can delete own profile" ON profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;

-- Create policies
-- Allow anyone to create a profile during signup
CREATE POLICY "Allow initial profile creation"
    ON profiles
    FOR INSERT
    WITH CHECK (true);  -- Allow any insert, foreign key will ensure valid user_id

-- Allow users to view their own profile
CREATE POLICY "Users can view own profile"
    ON profiles
    FOR SELECT
    USING (auth.uid() = user_id OR auth.role() = 'service_role');

-- Allow users to update their own profile
CREATE POLICY "Users can update own profile"
    ON profiles
    FOR UPDATE
    USING (auth.uid() = user_id OR auth.role() = 'service_role');

-- Allow users to delete their own profile
CREATE POLICY "Users can delete own profile"
    ON profiles
    FOR DELETE
    USING (auth.uid() = user_id OR auth.role() = 'service_role');

-- Allow public read access to certain profile fields (if needed)
-- CREATE POLICY "Public profiles are viewable"
--     ON profiles
--     FOR SELECT
--     USING (is_public = true);