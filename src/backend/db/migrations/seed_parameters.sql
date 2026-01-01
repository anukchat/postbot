-- Seed Parameters
-- This file seeds the parameters table with default parameters used by prompts

INSERT INTO parameters (parameter_id, name, display_name, description, is_required, created_at) VALUES
(gen_random_uuid(), 'persona', 'Persona', 'The persona/role for content generation (e.g., "content creator", "technical writer")', true, NOW()),
(gen_random_uuid(), 'content_type', 'Content Type', 'The type of content to generate (e.g., "blog post", "article", "tutorial")', true, NOW()),
(gen_random_uuid(), 'age_group', 'Age Group', 'Target age group for the content (e.g., "adults", "teens", "professionals")', true, NOW()),
(gen_random_uuid(), 'tone', 'Tone', 'Writing tone (e.g., "professional", "casual", "friendly")', false, NOW()),
(gen_random_uuid(), 'length', 'Length', 'Expected content length (e.g., "short", "medium", "long")', false, NOW())
ON CONFLICT (name) DO NOTHING;

-- Verify parameters
SELECT 'Seeded ' || COUNT(*) || ' parameters' as status FROM parameters;
