-- Data Uploader Database Schema

-- Projects/Buckets table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL UNIQUE,
    bucket_name VARCHAR(255) NOT NULL UNIQUE,
    aws_region VARCHAR(50) NOT NULL DEFAULT 'eu-west-1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sync Sessions table
CREATE TABLE IF NOT EXISTS sync_sessions (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    local_directory TEXT NOT NULL,
    s3_prefix VARCHAR(50) NOT NULL,
    aws_profile VARCHAR(100) NOT NULL,
    max_workers INTEGER DEFAULT 15,
    times_to_retry INTEGER DEFAULT 3,
    use_find BOOLEAN DEFAULT TRUE,
    status VARCHAR(50) DEFAULT 'in_progress',
    total_files INTEGER DEFAULT 0,
    total_size_bytes BIGINT DEFAULT 0,
    files_uploaded INTEGER DEFAULT 0,
    files_failed INTEGER DEFAULT 0,
    files_skipped INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- File Upload Records table
CREATE TABLE IF NOT EXISTS file_uploads (
    id BIGSERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sync_sessions(id) ON DELETE CASCADE,
    local_path TEXT NOT NULL,
    s3_key TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    uploaded_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Configuration History table
CREATE TABLE IF NOT EXISTS config_history (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sync_sessions(id) ON DELETE CASCADE,
    config_json JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_file_uploads_session_id ON file_uploads(session_id);
CREATE INDEX IF NOT EXISTS idx_file_uploads_status ON file_uploads(status);
CREATE INDEX IF NOT EXISTS idx_file_uploads_s3_key ON file_uploads(s3_key);
CREATE INDEX IF NOT EXISTS idx_sync_sessions_project_id ON sync_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_sync_sessions_status ON sync_sessions(status);

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update timestamp triggers
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_file_uploads_updated_at BEFORE UPDATE ON file_uploads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert example project (optional)
-- INSERT INTO projects (project_name, bucket_name, aws_region)
-- VALUES ('Example Project', 'example-bucket', 'eu-west-1');
