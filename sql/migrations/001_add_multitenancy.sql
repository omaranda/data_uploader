-- Migration: Add Multi-Tenancy Support
-- Description: Adds companies, users, cycles tables and extends existing tables for multi-tenant architecture
-- Date: 2025-12-25
-- Version: 001

-- ============================================================================
-- PART 1: CREATE NEW TABLES
-- ============================================================================

-- Companies table (client organizations)
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL UNIQUE,
    company_code VARCHAR(50) NOT NULL UNIQUE,
    contact_email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for companies
CREATE INDEX IF NOT EXISTS idx_companies_company_code ON companies(company_code);
CREATE INDEX IF NOT EXISTS idx_companies_is_active ON companies(is_active);

-- Users table (employees of companies)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for users
CREATE INDEX IF NOT EXISTS idx_users_company_id ON users(company_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Cycles table (structured cycle management)
CREATE TABLE IF NOT EXISTS cycles (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    cycle_name VARCHAR(50) NOT NULL,
    cycle_number INTEGER NOT NULL,
    s3_prefix VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    description TEXT,
    metadata JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(project_id, cycle_name),
    UNIQUE(project_id, cycle_number)
);

-- Create indexes for cycles
CREATE INDEX IF NOT EXISTS idx_cycles_project_id ON cycles(project_id);
CREATE INDEX IF NOT EXISTS idx_cycles_status ON cycles(status);
CREATE INDEX IF NOT EXISTS idx_cycles_cycle_number ON cycles(cycle_number);

-- ============================================================================
-- PART 2: EXTEND EXISTING TABLES
-- ============================================================================

-- Add company_id to projects table (nullable initially for migration)
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE;

-- Add description and is_active to projects
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS description TEXT;

ALTER TABLE projects
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE NOT NULL;

-- Create index for projects.company_id
CREATE INDEX IF NOT EXISTS idx_projects_company_id ON projects(company_id);
CREATE INDEX IF NOT EXISTS idx_projects_is_active ON projects(is_active);

-- Add cycle_id and user_id to sync_sessions table
ALTER TABLE sync_sessions
ADD COLUMN IF NOT EXISTS cycle_id INTEGER REFERENCES cycles(id) ON DELETE SET NULL;

ALTER TABLE sync_sessions
ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;

-- Create indexes for sync_sessions
CREATE INDEX IF NOT EXISTS idx_sync_sessions_cycle_id ON sync_sessions(cycle_id);
CREATE INDEX IF NOT EXISTS idx_sync_sessions_user_id ON sync_sessions(user_id);

-- ============================================================================
-- PART 3: CREATE TRIGGERS FOR AUTO-UPDATE TIMESTAMPS
-- ============================================================================

-- Trigger function for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to companies
DROP TRIGGER IF EXISTS update_companies_updated_at ON companies;
CREATE TRIGGER update_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to users
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to cycles
DROP TRIGGER IF EXISTS update_cycles_updated_at ON cycles;
CREATE TRIGGER update_cycles_updated_at
    BEFORE UPDATE ON cycles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- PART 4: DATA MIGRATION (if running on existing database)
-- ============================================================================

-- Note: The following migration steps are idempotent and safe to re-run

-- Create default company if it doesn't exist
DO $$
DECLARE
    default_company_id INTEGER;
BEGIN
    -- Insert default company or get existing
    INSERT INTO companies (company_name, company_code, contact_email, is_active)
    VALUES ('Default Company', 'DEFAULT', 'admin@example.com', TRUE)
    ON CONFLICT (company_code) DO NOTHING;

    -- Get the default company ID
    SELECT id INTO default_company_id FROM companies WHERE company_code = 'DEFAULT';

    -- Migrate existing projects to default company
    UPDATE projects
    SET company_id = default_company_id
    WHERE company_id IS NULL;

    -- Create cycles from existing sync_sessions
    -- This parses s3_prefix values like "C1", "C2", "C3", etc.
    INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, started_at, completed_at, created_at)
    SELECT DISTINCT
        ss.project_id,
        ss.s3_prefix as cycle_name,
        CAST(NULLIF(regexp_replace(ss.s3_prefix, '[^0-9]', '', 'g'), '') AS INTEGER) as cycle_number,
        ss.s3_prefix,
        CASE
            WHEN ss.status = 'completed' THEN 'completed'
            WHEN ss.status = 'in_progress' THEN 'in_progress'
            WHEN ss.status = 'failed' THEN 'incomplete'
            ELSE 'pending'
        END as status,
        MIN(ss.started_at) as started_at,
        MAX(ss.completed_at) as completed_at,
        MIN(ss.created_at) as created_at
    FROM sync_sessions ss
    WHERE ss.s3_prefix IS NOT NULL
      AND ss.s3_prefix ~ '^C[0-9]+$'  -- Only match C1, C2, C3, etc.
    GROUP BY ss.project_id, ss.s3_prefix, ss.status
    ON CONFLICT (project_id, cycle_name) DO NOTHING;

    -- Link existing sessions to cycles
    UPDATE sync_sessions ss
    SET cycle_id = c.id
    FROM cycles c
    WHERE c.project_id = ss.project_id
      AND c.s3_prefix = ss.s3_prefix
      AND ss.cycle_id IS NULL;

END $$;

-- ============================================================================
-- PART 5: ADD CONSTRAINTS (after data migration)
-- ============================================================================

-- Now we can make company_id NOT NULL since all existing projects are migrated
ALTER TABLE projects
ALTER COLUMN company_id SET NOT NULL;

-- ============================================================================
-- PART 6: CREATE VIEWS FOR REPORTING (OPTIONAL)
-- ============================================================================

-- View: Project summary with company info
CREATE OR REPLACE VIEW v_project_summary AS
SELECT
    p.id as project_id,
    p.project_name,
    p.bucket_name,
    p.aws_region,
    p.description,
    p.is_active,
    c.id as company_id,
    c.company_name,
    c.company_code,
    COUNT(DISTINCT cy.id) as total_cycles,
    COUNT(DISTINCT ss.id) as total_sessions,
    p.created_at,
    p.updated_at
FROM projects p
JOIN companies c ON p.company_id = c.id
LEFT JOIN cycles cy ON p.id = cy.project_id
LEFT JOIN sync_sessions ss ON p.id = ss.project_id
GROUP BY p.id, c.id;

-- View: Cycle summary with stats
CREATE OR REPLACE VIEW v_cycle_summary AS
SELECT
    cy.id as cycle_id,
    cy.cycle_name,
    cy.cycle_number,
    cy.status,
    cy.project_id,
    p.project_name,
    p.bucket_name,
    COUNT(DISTINCT ss.id) as total_sessions,
    SUM(COALESCE(ss.total_files, 0)) as total_files,
    SUM(COALESCE(ss.files_uploaded, 0)) as files_uploaded,
    SUM(COALESCE(ss.files_failed, 0)) as files_failed,
    SUM(COALESCE(ss.total_size_bytes, 0)) as total_size_bytes,
    cy.started_at,
    cy.completed_at
FROM cycles cy
JOIN projects p ON cy.project_id = p.id
LEFT JOIN sync_sessions ss ON cy.id = ss.cycle_id
GROUP BY cy.id, p.id;

-- ============================================================================
-- VERIFICATION QUERIES (for testing after migration)
-- ============================================================================

-- Verify companies
-- SELECT * FROM companies;

-- Verify users (should be empty initially, seed data creates admin)
-- SELECT * FROM users;

-- Verify projects have company_id
-- SELECT id, project_name, company_id FROM projects;

-- Verify cycles were created
-- SELECT * FROM cycles ORDER BY project_id, cycle_number;

-- Verify sessions linked to cycles
-- SELECT id, project_id, s3_prefix, cycle_id FROM sync_sessions WHERE s3_prefix ~ '^C[0-9]+$' LIMIT 10;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Log migration completion
DO $$
BEGIN
    RAISE NOTICE 'Migration 001_add_multitenancy.sql completed successfully';
    RAISE NOTICE 'Created tables: companies, users, cycles';
    RAISE NOTICE 'Extended tables: projects (company_id, description, is_active), sync_sessions (cycle_id, user_id)';
    RAISE NOTICE 'Next step: Run seed_data.sql to create default admin user';
END $$;
