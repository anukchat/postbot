-- Seed Reference Data
-- This file contains all the standard reference data required for the application
-- NOTE: This is now included in Alembic migration cf32c51cc0a1_add_checkpoint_tables_and_seed_data
-- Run this only if you need to re-seed data manually

-- ============================================================================
-- 1. GENERATION LIMITS
-- ============================================================================
INSERT INTO generation_limits (tier, max_generations) VALUES
('free', 5),
('basic', 20),
('premium', 1000)
ON CONFLICT (tier) DO UPDATE
SET max_generations = EXCLUDED.max_generations;

-- ============================================================================
-- 2. SOURCE TYPES
-- ============================================================================
INSERT INTO source_types (source_type_id, name, created_at) VALUES
('9adce6f3-b254-47f5-8a7a-96fe8604488e', 'twitter', NOW()),
('27c67d4f-d400-4883-9131-6c3d510ed11a', 'web_url', NOW()),
('ec5df507-74f0-478f-9a8f-46420423dacb', 'topic', NOW()),
('eac4b028-3064-44a9-8773-62dade8bd0ea', 'reddit', NOW())
ON CONFLICT (source_type_id) DO NOTHING;

-- ============================================================================
-- 3. CONTENT TYPES
-- ============================================================================
INSERT INTO content_types (content_type_id, name, created_at) VALUES
(gen_random_uuid(), 'blog', NOW()),
(gen_random_uuid(), 'social_post', NOW()),
(gen_random_uuid(), 'article', NOW()),
(gen_random_uuid(), 'newsletter', NOW())
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- 4. PARAMETERS
-- ============================================================================
INSERT INTO parameters (parameter_id, name, display_name, description, is_required, created_at) VALUES
(gen_random_uuid(), 'persona', 'Persona', 'The persona/role for content generation (e.g., "content creator", "technical writer")', true, NOW()),
(gen_random_uuid(), 'content_type', 'Content Type', 'The type of content to generate (e.g., "blog post", "article", "tutorial")', true, NOW()),
(gen_random_uuid(), 'age_group', 'Age Group', 'Target age group for the content (e.g., "adults", "teens", "professionals")', true, NOW()),
(gen_random_uuid(), 'tone', 'Tone', 'Writing tone (e.g., "professional", "casual", "friendly")', false, NOW()),
(gen_random_uuid(), 'length', 'Length', 'Expected content length (e.g., "short", "medium", "long")', false, NOW())
ON CONFLICT (name) DO NOTHING;

-- Verify the seed data
DO $$
DECLARE
    gen_limits_count INTEGER;
    source_types_count INTEGER;
    content_types_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO gen_limits_count FROM generation_limits;
    SELECT COUNT(*) INTO source_types_count FROM source_types;
    SELECT COUNT(*) INTO content_types_count FROM content_types;
    
    RAISE NOTICE 'Seed data verification:';
    RAISE NOTICE '  - Generation Limits: % rows', gen_limits_count;
    RAISE NOTICE '  - Source Types: % rows', source_types_count;
    RAISE NOTICE '  - Content Types: % rows', content_types_count;
    
    IF gen_limits_count < 3 THEN
        RAISE WARNING 'Expected 3 generation limit tiers, found %', gen_limits_count;
    END IF;
    
    IF source_types_count < 4 THEN
        RAISE WARNING 'Expected 4 source types, found %', source_types_count;
    END IF;
END $$;
