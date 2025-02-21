-- Function to reset generation counts
CREATE OR REPLACE FUNCTION reset_monthly_generations()
RETURNS void AS $$
BEGIN
    UPDATE profiles 
    SET generations_used = 0,
        updated_at = NOW()
    WHERE role IN (SELECT tier FROM generation_limits);
END;
$$ LANGUAGE plpgsql;

-- Create a cron job to run monthly
SELECT cron.schedule('0 0 1 * *', $$SELECT reset_monthly_generations()$$);
