-- Seed Data Script
-- Description: Creates default company and admin user for initial setup
-- Date: 2025-12-25
-- Note: This script is idempotent and safe to re-run

-- ============================================================================
-- CREATE DEFAULT ADMIN USER
-- ============================================================================

DO $$
DECLARE
    default_company_id INTEGER;
    admin_exists BOOLEAN;
BEGIN
    -- Get the default company ID
    SELECT id INTO default_company_id
    FROM companies
    WHERE company_code = 'DEFAULT';

    IF default_company_id IS NULL THEN
        RAISE EXCEPTION 'Default company not found. Run migration 001_add_multitenancy.sql first.';
    END IF;

    -- Check if admin user already exists
    SELECT EXISTS(SELECT 1 FROM users WHERE username = 'admin') INTO admin_exists;

    IF NOT admin_exists THEN
        -- Create default admin user
        -- Default password: 'admin123' (CHANGE THIS IN PRODUCTION!)
        -- Password hash generated with bcrypt (rounds=12)
        -- You should change this password immediately after first login
        INSERT INTO users (
            company_id,
            username,
            email,
            password_hash,
            full_name,
            role,
            is_active
        ) VALUES (
            default_company_id,
            'admin',
            'admin@example.com',
            '$2b$12$zXsu1RYL4hoRPVvARL78KeIyhWLY.RhsMT81EEVeYntbu9vDolmMS',  -- bcrypt hash of 'admin123'
            'System Administrator',
            'admin',
            TRUE
        );

        RAISE NOTICE 'Default admin user created';
        RAISE NOTICE 'Username: admin';
        RAISE NOTICE 'Password: admin123';
        RAISE NOTICE 'WARNING: Change this password immediately in production!';
    ELSE
        RAISE NOTICE 'Admin user already exists, skipping creation';
    END IF;

END $$;

-- ============================================================================
-- CREATE EXAMPLE DATA (OPTIONAL - comment out if not needed)
-- ============================================================================

/*
DO $$
DECLARE
    default_company_id INTEGER;
    example_project_id INTEGER;
BEGIN
    -- Get default company
    SELECT id INTO default_company_id FROM companies WHERE company_code = 'DEFAULT';

    -- Create example project if it doesn't exist
    INSERT INTO projects (company_id, project_name, bucket_name, aws_region, description, is_active)
    VALUES (
        default_company_id,
        'Example Project',
        'example-data-bucket',
        'eu-west-1',
        'Example project for testing the upload system',
        TRUE
    )
    ON CONFLICT (project_name) DO NOTHING
    RETURNING id INTO example_project_id;

    -- If project was just created, add some example cycles
    IF example_project_id IS NOT NULL THEN
        -- Create 4 example cycles
        INSERT INTO cycles (project_id, cycle_name, cycle_number, s3_prefix, status, description)
        VALUES
            (example_project_id, 'C1', 1, 'C1', 'pending', 'First data collection cycle'),
            (example_project_id, 'C2', 2, 'C2', 'pending', 'Second data collection cycle'),
            (example_project_id, 'C3', 3, 'C3', 'pending', 'Third data collection cycle'),
            (example_project_id, 'C4', 4, 'C4', 'pending', 'Fourth data collection cycle');

        RAISE NOTICE 'Example project and cycles created';
    END IF;

END $$;
*/

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Display created users
SELECT
    u.id,
    u.username,
    u.email,
    u.full_name,
    u.role,
    c.company_name,
    u.is_active,
    u.created_at
FROM users u
JOIN companies c ON u.company_id = c.id
ORDER BY u.id;

-- ============================================================================
-- SEED DATA COMPLETE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '==================================================';
    RAISE NOTICE 'Seed data script completed';
    RAISE NOTICE '==================================================';
    RAISE NOTICE 'Default admin credentials:';
    RAISE NOTICE '  Username: admin';
    RAISE NOTICE '  Password: admin123';
    RAISE NOTICE '';
    RAISE NOTICE 'IMPORTANT SECURITY NOTES:';
    RAISE NOTICE '1. Change the admin password immediately';
    RAISE NOTICE '2. Create new admin users with strong passwords';
    RAISE NOTICE '3. Disable the default admin account in production';
    RAISE NOTICE '==================================================';
END $$;
