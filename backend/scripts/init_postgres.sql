-- Psi PostgreSQL Database Initialization Script
-- Creates all necessary tables and indexes for the application

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    profile_pic_url VARCHAR(500),
    subscription_type VARCHAR(20) DEFAULT 'free' CHECK (subscription_type IN ('free', 'premium')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Food Records Table
CREATE TABLE IF NOT EXISTS food_records (
    record_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    image_url VARCHAR(500),
    foods JSONB NOT NULL,
    total_calories DECIMAL(10, 2) NOT NULL,
    nutrition JSONB,
    emotion_state VARCHAR(50),
    emotion_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Emotion Data Table
CREATE TABLE IF NOT EXISTS emotion_data (
    emotion_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    hrv DECIMAL(10, 2) NOT NULL,
    heart_rate INTEGER NOT NULL,
    coherence DECIMAL(3, 2),
    emotion_type VARCHAR(50) NOT NULL,
    emotion_score INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_emotion FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Recipes Table
CREATE TABLE IF NOT EXISTS recipes (
    recipe_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    ingredients JSONB NOT NULL,
    instructions JSONB NOT NULL,
    cooking_time INTEGER,
    difficulty VARCHAR(20) CHECK (difficulty IN ('easy', 'medium', 'hard')),
    emotion_type VARCHAR(50),
    nutrition JSONB,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Sessions Table (for JWT tracking)
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT true
);

-- Daily Usage Tracking (for free tier limits)
CREATE TABLE IF NOT EXISTS daily_usage (
    usage_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    food_analyses INTEGER DEFAULT 0,
    fridge_analyses INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

-- Indexes for Performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_food_records_user ON food_records(user_id);
CREATE INDEX idx_food_records_created ON food_records(created_at DESC);
CREATE INDEX idx_emotion_data_user_time ON emotion_data(user_id, timestamp DESC);
CREATE INDEX idx_emotion_data_timestamp ON emotion_data(timestamp DESC);
CREATE INDEX idx_recipes_emotion ON recipes(emotion_type);
CREATE INDEX idx_user_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_active ON user_sessions(is_active);
CREATE INDEX idx_daily_usage_user_date ON daily_usage(user_id, date);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample recipes (for testing)
INSERT INTO recipes (name, ingredients, instructions, cooking_time, difficulty, emotion_type, nutrition) VALUES
('Simple Pasta',
 '[{"name": "pasta", "quantity": "200", "unit": "g"}, {"name": "tomato sauce", "quantity": "100", "unit": "g"}, {"name": "garlic", "quantity": "2", "unit": "cloves"}]',
 '[{"step_number": 1, "instruction": "Boil water", "duration_minutes": 2}, {"step_number": 2, "instruction": "Cook pasta", "duration_minutes": 10}, {"step_number": 3, "instruction": "Add sauce", "duration_minutes": 3}]',
 15, 'easy', 'stress',
 '{"calories": 350, "protein": 12, "carbs": 68, "fat": 4}'),

('Comfort Soup',
 '[{"name": "chicken broth", "quantity": "500", "unit": "ml"}, {"name": "vegetables", "quantity": "200", "unit": "g"}]',
 '[{"step_number": 1, "instruction": "Heat broth", "duration_minutes": 5}, {"step_number": 2, "instruction": "Add vegetables", "duration_minutes": 10}]',
 15, 'easy', 'fatigue',
 '{"calories": 180, "protein": 8, "carbs": 25, "fat": 2}'),

('Energy Bowl',
 '[{"name": "quinoa", "quantity": "100", "unit": "g"}, {"name": "avocado", "quantity": "1", "unit": "piece"}, {"name": "eggs", "quantity": "2", "unit": "pieces"}]',
 '[{"step_number": 1, "instruction": "Cook quinoa", "duration_minutes": 15}, {"step_number": 2, "instruction": "Fry eggs", "duration_minutes": 5}, {"step_number": 3, "instruction": "Assemble bowl", "duration_minutes": 2}]',
 22, 'medium', 'focus',
 '{"calories": 520, "protein": 22, "carbs": 45, "fat": 28}');

-- Print success message
DO $$
BEGIN
    RAISE NOTICE 'Psi database initialized successfully!';
END $$;
