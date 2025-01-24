-- First drop the existing foreign key constraint on profiles.id
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_id_fkey;

-- First create a default profile
DO $$
DECLARE
    new_profile_id UUID := gen_random_uuid();
    existing_user_id UUID := '4f4f77b5-7545-4af1-add2-98e275ac9413'::UUID;
BEGIN
    -- Insert profile with random id and existing user_id
    INSERT INTO profiles (id, user_id, full_name, role, subscription_status)
    VALUES (new_profile_id, existing_user_id, 'Anukool Chaturvedi', 'free', 'none')
    ON CONFLICT (user_id) DO NOTHING
    RETURNING id INTO new_profile_id;

    -- If there was a conflict, get the existing profile id
    IF NOT FOUND THEN
        SELECT id INTO new_profile_id FROM profiles WHERE user_id = existing_user_id;
    END IF;

    -- Update all content records where profile_id is null
    UPDATE content 
    SET profile_id = new_profile_id
    WHERE profile_id IS NULL;

    -- Now make the column NOT NULL
    ALTER TABLE content 
    ALTER COLUMN profile_id SET NOT NULL;
END $$;
