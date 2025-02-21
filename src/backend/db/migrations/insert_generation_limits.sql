INSERT INTO generation_limits (tier, max_generations) VALUES
('free', 10),
('basic', 50),
('premium', 100)
ON CONFLICT (tier) DO UPDATE
SET max_generations = EXCLUDED.max_generations;
