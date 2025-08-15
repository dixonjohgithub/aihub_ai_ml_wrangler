-- Database initialization script
-- This file is automatically executed when PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create additional schemas if needed
-- CREATE SCHEMA IF NOT EXISTS analytics;
-- CREATE SCHEMA IF NOT EXISTS logs;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE aihub_dev TO aihub_user;
GRANT ALL PRIVILEGES ON DATABASE aihub_prod TO aihub_user;

-- Create initial tables (example)
-- This should be replaced with actual migration files in production

-- Example: Users table
-- CREATE TABLE IF NOT EXISTS users (
--     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--     email VARCHAR(255) UNIQUE NOT NULL,
--     username VARCHAR(100) UNIQUE NOT NULL,
--     password_hash VARCHAR(255) NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- Example: Sessions table
-- CREATE TABLE IF NOT EXISTS user_sessions (
--     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--     user_id UUID REFERENCES users(id) ON DELETE CASCADE,
--     session_token VARCHAR(255) UNIQUE NOT NULL,
--     expires_at TIMESTAMP NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- Insert sample data for development
-- INSERT INTO users (email, username, password_hash) 
-- VALUES ('admin@aihub.com', 'admin', crypt('admin123', gen_salt('bf')))
-- ON CONFLICT (email) DO NOTHING;

-- Log initialization
\echo 'Database initialization completed successfully';