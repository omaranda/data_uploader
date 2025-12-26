# Database Schema Documentation

## Overview

Multi-tenant PostgreSQL database schema for the data uploader system with company-scoped access control.

**Database:** PostgreSQL 16
**Location:** docker-compose service on port 5432

---

## Entity Relationship Diagram

```
companies (1) ──< (N) users
    │
    └──< (N) projects ──< (N) cycles
                 │
                 └──< (N) sync_sessions ──< (N) file_uploads
                            ↑
                            │
                       user_id (FK)
                       cycle_id (FK)
```

---

## Tables

### companies

Client organizations in the multi-tenant system.

**Columns:**
- `id` (SERIAL, PK) - Primary key
- `company_name` (VARCHAR(255), UNIQUE, NOT NULL) - Company name
- `company_code` (VARCHAR(50), UNIQUE, NOT NULL) - Short code for company
- `contact_email` (VARCHAR(255)) - Contact email
- `is_active` (BOOLEAN, NOT NULL, DEFAULT TRUE) - Active status
- `created_at` (TIMESTAMP, NOT NULL) - Creation timestamp
- `updated_at` (TIMESTAMP, NOT NULL) - Last update timestamp

**Indexes:**
- `idx_companies_company_code` on `company_code`
- `idx_companies_is_active` on `is_active`

**Relationships:**
- One-to-many with `users`
- One-to-many with `projects`

---

### users

Employees of companies with authentication credentials.

**Columns:**
- `id` (SERIAL, PK) - Primary key
- `company_id` (INTEGER, FK, NOT NULL) - References companies(id)
- `username` (VARCHAR(100), UNIQUE, NOT NULL) - Login username
- `email` (VARCHAR(255), UNIQUE, NOT NULL) - Email address
- `password_hash` (VARCHAR(255), NOT NULL) - Bcrypt password hash
- `full_name` (VARCHAR(255)) - Full name
- `role` (VARCHAR(50), NOT NULL, DEFAULT 'user') - Role: 'admin' or 'user'
- `is_active` (BOOLEAN, NOT NULL, DEFAULT TRUE) - Active status
- `last_login` (TIMESTAMP) - Last login timestamp
- `created_at` (TIMESTAMP, NOT NULL) - Creation timestamp
- `updated_at` (TIMESTAMP, NOT NULL) - Last update timestamp

**Indexes:**
- `idx_users_company_id` on `company_id`
- `idx_users_username` on `username`
- `idx_users_email` on `email`
- `idx_users_is_active` on `is_active`
- `idx_users_role` on `role`

**Constraints:**
- Foreign key to `companies(id)` with CASCADE delete

**Relationships:**
- Many-to-one with `companies`
- One-to-many with `sync_sessions`

---

### projects

S3 upload projects managed by companies.

**Columns:**
- `id` (SERIAL, PK) - Primary key
- `company_id` (INTEGER, FK, NOT NULL) - References companies(id)
- `project_name` (VARCHAR(255), UNIQUE, NOT NULL) - Project name
- `bucket_name` (VARCHAR(255), NOT NULL) - S3 bucket name
- `aws_region` (VARCHAR(50), NOT NULL) - AWS region
- `description` (TEXT) - Project description
- `is_active` (BOOLEAN, NOT NULL, DEFAULT TRUE) - Active status
- `created_at` (TIMESTAMP, NOT NULL) - Creation timestamp
- `updated_at` (TIMESTAMP, NOT NULL) - Last update timestamp

**Indexes:**
- `idx_projects_company_id` on `company_id`
- `idx_projects_is_active` on `is_active`

**Constraints:**
- Foreign key to `companies(id)` with CASCADE delete

**Relationships:**
- Many-to-one with `companies`
- One-to-many with `cycles`
- One-to-many with `sync_sessions`

---

### cycles

Structured data collection cycles for projects (C1, C2, C3, etc.).

**Columns:**
- `id` (SERIAL, PK) - Primary key
- `project_id` (INTEGER, FK, NOT NULL) - References projects(id)
- `cycle_name` (VARCHAR(50), NOT NULL) - Cycle name (e.g., "C1", "C2")
- `cycle_number` (INTEGER, NOT NULL) - Numeric cycle identifier (1, 2, 3...)
- `s3_prefix` (VARCHAR(100), NOT NULL) - S3 key prefix for this cycle
- `status` (VARCHAR(50), NOT NULL, DEFAULT 'pending') - Status
- `description` (TEXT) - Cycle description
- `metadata` (JSONB) - Additional metadata
- `started_at` (TIMESTAMP) - Cycle start timestamp
- `completed_at` (TIMESTAMP) - Cycle completion timestamp
- `created_at` (TIMESTAMP, NOT NULL) - Creation timestamp
- `updated_at` (TIMESTAMP, NOT NULL) - Last update timestamp

**Status Values:**
- `pending` - Not started
- `in_progress` - Currently uploading
- `completed` - Successfully completed
- `incomplete` - Partially completed or failed

**Indexes:**
- `idx_cycles_project_id` on `project_id`
- `idx_cycles_status` on `status`
- `idx_cycles_cycle_number` on `cycle_number`

**Constraints:**
- Foreign key to `projects(id)` with CASCADE delete
- Unique constraint on `(project_id, cycle_name)`
- Unique constraint on `(project_id, cycle_number)`

**Relationships:**
- Many-to-one with `projects`
- One-to-many with `sync_sessions`

---

### sync_sessions

Individual upload sessions tracking progress and statistics.

**Columns:**
- `id` (SERIAL, PK) - Primary key
- `project_id` (INTEGER, FK, NOT NULL) - References projects(id)
- `cycle_id` (INTEGER, FK) - References cycles(id), nullable for backward compatibility
- `user_id` (INTEGER, FK) - References users(id), nullable for CLI uploads
- `s3_prefix` (VARCHAR(100)) - S3 key prefix (kept for backward compatibility)
- `status` (VARCHAR(50), NOT NULL, DEFAULT 'pending') - Upload status
- `total_files` (INTEGER, DEFAULT 0) - Total files to upload
- `files_uploaded` (INTEGER, DEFAULT 0) - Successfully uploaded files
- `files_failed` (INTEGER, DEFAULT 0) - Failed uploads
- `files_skipped` (INTEGER, DEFAULT 0) - Skipped files (duplicates)
- `total_size_bytes` (BIGINT, DEFAULT 0) - Total size in bytes
- `uploaded_size_bytes` (BIGINT, DEFAULT 0) - Uploaded size in bytes
- `started_at` (TIMESTAMP) - Session start timestamp
- `completed_at` (TIMESTAMP) - Session completion timestamp
- `error_message` (VARCHAR(500)) - Error message if failed
- `created_at` (TIMESTAMP, NOT NULL) - Creation timestamp

**Status Values:**
- `pending` - Queued, not started
- `in_progress` - Currently uploading
- `completed` - Successfully completed
- `failed` - Failed with errors

**Indexes:**
- `idx_sync_sessions_project_id` on `project_id`
- `idx_sync_sessions_cycle_id` on `cycle_id`
- `idx_sync_sessions_user_id` on `user_id`
- `idx_sync_sessions_status` on `status`
- `idx_sync_sessions_created_at` on `created_at`

**Constraints:**
- Foreign key to `projects(id)` with CASCADE delete
- Foreign key to `cycles(id)` with SET NULL
- Foreign key to `users(id)` with SET NULL

**Relationships:**
- Many-to-one with `projects`
- Many-to-one with `cycles` (optional)
- Many-to-one with `users` (optional)
- One-to-many with `file_uploads`

---

### file_uploads

Individual file upload records with status and metadata.

**Columns:**
- `id` (SERIAL, PK) - Primary key
- `session_id` (INTEGER, FK, NOT NULL) - References sync_sessions(id)
- `file_path` (VARCHAR(1024), NOT NULL) - Local file path
- `s3_key` (VARCHAR(1024), NOT NULL) - S3 object key
- `file_size` (BIGINT) - File size in bytes
- `checksum` (VARCHAR(64)) - File checksum (MD5/SHA256)
- `status` (VARCHAR(50), NOT NULL, DEFAULT 'pending') - Upload status
- `error_message` (VARCHAR(500)) - Error message if failed
- `uploaded_at` (TIMESTAMP) - Upload completion timestamp
- `is_duplicate` (BOOLEAN, DEFAULT FALSE) - Whether file is a duplicate
- `created_at` (TIMESTAMP, NOT NULL) - Creation timestamp

**Status Values:**
- `pending` - Not started
- `uploading` - Currently uploading
- `completed` - Successfully uploaded
- `failed` - Upload failed
- `skipped` - Skipped (duplicate)

**Indexes:**
- `idx_file_uploads_session_id` on `session_id`
- `idx_file_uploads_s3_key` on `s3_key`
- `idx_file_uploads_status` on `status`
- `idx_file_uploads_created_at` on `created_at`

**Constraints:**
- Foreign key to `sync_sessions(id)` with CASCADE delete

**Relationships:**
- Many-to-one with `sync_sessions`

---

## Views

### v_project_summary

Summary view of projects with statistics.

```sql
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
```

### v_cycle_summary

Summary view of cycles with upload statistics.

```sql
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
```

---

## Default Data

### Default Company
- **company_name**: "Default Company"
- **company_code**: "DEFAULT"
- **contact_email**: "admin@example.com"

### Default Admin User
- **username**: "admin"
- **password**: "admin123" (⚠️ **CHANGE IN PRODUCTION**)
- **email**: "admin@example.com"
- **full_name**: "System Administrator"
- **role**: "admin"

---

Last Updated: December 25, 2025
