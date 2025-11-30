-- Migration: Create daily_usage table for rate limiting
-- Date: 2025-11-10
-- Description: Adds table for tracking daily API usage per user for free tier limits

-- Create daily_usage table
CREATE TABLE IF NOT EXISTS daily_usage (
    usage_id UUID PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    food_analyses INTEGER DEFAULT 0,
    fridge_analyses INTEGER DEFAULT 0,
    wellness_checks INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Ensure one record per user per day
    CONSTRAINT unique_user_date UNIQUE(user_id, date)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_daily_usage_user_date
    ON daily_usage(user_id, date);

CREATE INDEX IF NOT EXISTS idx_daily_usage_date
    ON daily_usage(date);

-- Create function to cleanup old records
CREATE OR REPLACE FUNCTION cleanup_old_daily_usage(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM daily_usage
    WHERE date < CURRENT_DATE - (days_to_keep || ' days')::INTERVAL;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Add comment
COMMENT ON TABLE daily_usage IS 'Tracks daily API usage per user for rate limiting';
COMMENT ON FUNCTION cleanup_old_daily_usage IS 'Deletes usage records older than specified days (default 30)';

-- Optional: Schedule daily cleanup (requires pg_cron extension)
-- To enable: CREATE EXTENSION IF NOT EXISTS pg_cron;
-- Then run: SELECT cron.schedule('cleanup-usage', '0 2 * * *', 'SELECT cleanup_old_daily_usage()');
