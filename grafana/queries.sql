-- =============================================================================
-- GRAFANA QUERIES FOR DATA UPLOADER DASHBOARD
-- =============================================================================
--
-- This file contains SQL queries optimized for Grafana dashboards to monitor
-- upload progress, track statistics, and identify issues.
--
-- Setup Instructions:
-- 1. Add PostgreSQL data source in Grafana
--    - Host: localhost:5432
--    - Database: data_uploader
--    - User: uploader
--    - Password: uploader_pass
-- 2. Import the dashboard JSON from this folder
-- 3. Or manually create panels using queries below
--
-- =============================================================================

-- =============================================================================
-- REAL-TIME MONITORING QUERIES (for CLI upload progress)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Active Upload Sessions (Table)
-- Purpose: Monitor currently running uploads in real-time
-- Panel Type: Table
-- Refresh: 5s (for real-time monitoring)
-- -----------------------------------------------------------------------------
SELECT
    ss.id AS "Session ID",
    c.company_name AS "Company",
    p.project_name AS "Project",
    ss.s3_prefix AS "Cycle",
    ss.total_files AS "Total Files",
    ss.files_uploaded AS "Uploaded",
    ss.files_failed AS "Failed",
    ss.files_skipped AS "Skipped",
    CASE
        WHEN ss.total_files > 0 THEN
            ROUND((ss.files_uploaded::numeric / ss.total_files * 100), 1)
        ELSE 0
    END AS "Progress %",
    ROUND(ss.total_size_bytes::numeric / (1024^3), 2) AS "Size (GB)",
    ROUND(
        EXTRACT(EPOCH FROM (NOW() - ss.started_at)) / 60,
        1
    ) AS "Duration (min)",
    CASE
        WHEN ss.total_files > 0 AND ss.files_uploaded > 0 THEN
            ROUND(
                ss.files_uploaded::numeric /
                NULLIF(EXTRACT(EPOCH FROM (NOW() - ss.started_at)), 0),
                2
            )
        ELSE 0
    END AS "Speed (files/s)",
    ss.started_at AS "Started"
FROM sync_sessions ss
JOIN projects p ON ss.project_id = p.id
JOIN companies c ON p.company_id = c.id
WHERE ss.status = 'in_progress'
ORDER BY ss.started_at DESC;


-- -----------------------------------------------------------------------------
-- 2. Upload Progress Gauge (for single active session)
-- Purpose: Show completion percentage for the most recent active upload
-- Panel Type: Gauge
-- Refresh: 5s
-- -----------------------------------------------------------------------------
SELECT
    CASE
        WHEN total_files > 0 THEN
            ROUND((files_uploaded::numeric / total_files * 100), 1)
        ELSE 0
    END AS "Progress %"
FROM sync_sessions
WHERE status = 'in_progress'
ORDER BY started_at DESC
LIMIT 1;


-- -----------------------------------------------------------------------------
-- 3. Current Upload Speed (Stat)
-- Purpose: Show real-time upload speed for active sessions
-- Panel Type: Stat
-- Refresh: 5s
-- Unit: files/s
-- -----------------------------------------------------------------------------
SELECT
    ROUND(
        AVG(
            files_uploaded::numeric /
            NULLIF(EXTRACT(EPOCH FROM (NOW() - started_at)), 0)
        ),
        2
    ) AS "Files per Second"
FROM sync_sessions
WHERE status = 'in_progress'
  AND started_at > NOW() - INTERVAL '1 hour';


-- -----------------------------------------------------------------------------
-- 4. Files Uploaded Today (Stat)
-- Purpose: Show total files uploaded in the current day
-- Panel Type: Stat
-- Refresh: 30s
-- -----------------------------------------------------------------------------
SELECT
    COUNT(*) AS "Files Uploaded Today"
FROM file_uploads
WHERE status = 'uploaded'
  AND uploaded_at >= DATE_TRUNC('day', NOW());


-- -----------------------------------------------------------------------------
-- 5. Recent Session Timeline (Bar Gauge)
-- Purpose: Show progress of recent sessions (completed or in progress)
-- Panel Type: Bar Gauge
-- Refresh: 30s
-- -----------------------------------------------------------------------------
SELECT
    CONCAT(p.project_name, ' - ', ss.s3_prefix, ' (ID: ', ss.id, ')') AS "Session",
    CASE
        WHEN ss.total_files > 0 THEN
            ROUND((ss.files_uploaded::numeric / ss.total_files * 100), 1)
        ELSE 0
    END AS "Progress %"
FROM sync_sessions ss
JOIN projects p ON ss.project_id = p.id
WHERE ss.started_at >= NOW() - INTERVAL '24 hours'
ORDER BY ss.started_at DESC
LIMIT 10;


-- =============================================================================
-- STATISTICS & ANALYTICS QUERIES
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 6. Total Files Per Project (Table)
-- Purpose: Overview of all projects with upload statistics
-- Panel Type: Table
-- Refresh: On Dashboard Load
-- -----------------------------------------------------------------------------
SELECT
    c.company_name AS "Company",
    p.project_name AS "Project",
    p.bucket_name AS "Bucket",
    COUNT(DISTINCT ss.id) AS "Sessions",
    COALESCE(SUM(ss.total_files), 0) AS "Total Files",
    COALESCE(SUM(ss.files_uploaded), 0) AS "Uploaded",
    COALESCE(SUM(ss.files_failed), 0) AS "Failed",
    ROUND(COALESCE(SUM(ss.total_size_bytes), 0)::numeric / (1024^3), 2) AS "Size (GB)",
    MAX(ss.started_at) AS "Last Upload"
FROM projects p
JOIN companies c ON p.company_id = c.id
LEFT JOIN sync_sessions ss ON p.id = ss.project_id
WHERE p.is_active = TRUE
GROUP BY c.company_name, p.project_name, p.bucket_name
ORDER BY "Last Upload" DESC NULLS LAST;


-- -----------------------------------------------------------------------------
-- 7. Files by Cycle Comparison (Bar Chart)
-- Purpose: Compare file quantities across different cycles
-- Panel Type: Bar Chart (Grouped/Stacked)
-- Variable: $bucket_name
-- Refresh: On Dashboard Load
-- -----------------------------------------------------------------------------
SELECT
    ss.s3_prefix AS "Cycle",
    fu.file_type AS "File Type",
    COUNT(*) AS "File Count"
FROM file_uploads fu
JOIN sync_sessions ss ON fu.session_id = ss.id
JOIN projects p ON ss.project_id = p.id
WHERE p.bucket_name = '${bucket_name:text}'
  AND fu.status = 'uploaded'
GROUP BY ss.s3_prefix, fu.file_type
ORDER BY ss.s3_prefix, fu.file_type;


-- -----------------------------------------------------------------------------
-- 8. Upload Success Rate Over Time (Time Series)
-- Purpose: Track upload success rate trend
-- Panel Type: Time Series
-- Refresh: 1m
-- -----------------------------------------------------------------------------
SELECT
    DATE_TRUNC('hour', uploaded_at) AS "time",
    ROUND(
        (SUM(CASE WHEN status = 'uploaded' THEN 1 ELSE 0 END)::numeric /
         NULLIF(COUNT(*), 0) * 100),
        2
    ) AS "Success Rate %"
FROM file_uploads
WHERE uploaded_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', uploaded_at)
ORDER BY "time";


-- -----------------------------------------------------------------------------
-- 9. File Type Distribution (Pie Chart)
-- Purpose: Show distribution of uploaded file types
-- Panel Type: Pie Chart
-- Refresh: On Dashboard Load
-- -----------------------------------------------------------------------------
SELECT
    UPPER(file_type) AS "File Type",
    COUNT(*) AS "Count"
FROM file_uploads
WHERE status = 'uploaded'
GROUP BY file_type
ORDER BY COUNT(*) DESC;


-- -----------------------------------------------------------------------------
-- 10. Failed Files Report (Table)
-- Purpose: List failed uploads with error details for troubleshooting
-- Panel Type: Table
-- Refresh: 1m
-- -----------------------------------------------------------------------------
SELECT
    p.project_name AS "Project",
    ss.s3_prefix AS "Cycle",
    fu.s3_key AS "File Path",
    fu.file_type AS "Type",
    ROUND(fu.file_size::numeric / (1024^2), 2) AS "Size (MB)",
    fu.retry_count AS "Retries",
    fu.error_message AS "Error",
    fu.updated_at AS "Last Attempt"
FROM file_uploads fu
JOIN sync_sessions ss ON fu.session_id = ss.id
JOIN projects p ON ss.project_id = p.id
WHERE fu.status = 'failed'
ORDER BY fu.updated_at DESC
LIMIT 100;


-- -----------------------------------------------------------------------------
-- 11. Session History (Table)
-- Purpose: Complete history of all upload sessions
-- Panel Type: Table
-- Refresh: 30s
-- -----------------------------------------------------------------------------
SELECT
    ss.id AS "ID",
    c.company_name AS "Company",
    p.project_name AS "Project",
    ss.s3_prefix AS "Cycle",
    ss.status AS "Status",
    ss.total_files AS "Total",
    ss.files_uploaded AS "Uploaded",
    ss.files_failed AS "Failed",
    ss.files_skipped AS "Skipped",
    ROUND(ss.total_size_bytes::numeric / (1024^3), 2) AS "Size (GB)",
    CASE
        WHEN ss.completed_at IS NOT NULL AND ss.started_at IS NOT NULL THEN
            ROUND(EXTRACT(EPOCH FROM (ss.completed_at - ss.started_at)) / 60, 1)
        WHEN ss.started_at IS NOT NULL THEN
            ROUND(EXTRACT(EPOCH FROM (NOW() - ss.started_at)) / 60, 1)
        ELSE NULL
    END AS "Duration (min)",
    ss.started_at AS "Started",
    ss.completed_at AS "Completed"
FROM sync_sessions ss
JOIN projects p ON ss.project_id = p.id
JOIN companies c ON p.company_id = c.id
ORDER BY ss.started_at DESC
LIMIT 100;


-- -----------------------------------------------------------------------------
-- 12. Upload Volume Over Time (Time Series)
-- Purpose: Visualize upload volume trends
-- Panel Type: Time Series (Area Chart)
-- Refresh: 1h
-- -----------------------------------------------------------------------------
SELECT
    DATE_TRUNC('day', uploaded_at) AS "time",
    COUNT(*) AS "Files Uploaded",
    ROUND(SUM(file_size)::numeric / (1024^3), 2) AS "Size (GB)"
FROM file_uploads
WHERE status = 'uploaded'
  AND uploaded_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', uploaded_at)
ORDER BY "time";


-- -----------------------------------------------------------------------------
-- 13. Average Upload Speed by Project (Table)
-- Purpose: Compare upload performance across projects
-- Panel Type: Table
-- Refresh: 1h
-- -----------------------------------------------------------------------------
SELECT
    p.project_name AS "Project",
    COUNT(ss.id) AS "Sessions",
    ROUND(
        AVG(
            ss.files_uploaded::numeric /
            NULLIF(EXTRACT(EPOCH FROM (ss.completed_at - ss.started_at)), 0)
        ),
        2
    ) AS "Avg Speed (files/s)",
    ROUND(
        AVG(
            ss.total_size_bytes::numeric /
            NULLIF(EXTRACT(EPOCH FROM (ss.completed_at - ss.started_at)), 0) /
            (1024^2)
        ),
        2
    ) AS "Avg Speed (MB/s)",
    ROUND(AVG(EXTRACT(EPOCH FROM (ss.completed_at - ss.started_at)) / 60), 1) AS "Avg Duration (min)"
FROM sync_sessions ss
JOIN projects p ON ss.project_id = p.id
WHERE ss.status IN ('completed', 'completed_with_errors')
  AND ss.completed_at >= NOW() - INTERVAL '30 days'
GROUP BY p.project_name
ORDER BY "Avg Speed (files/s)" DESC;


-- =============================================================================
-- DASHBOARD VARIABLES (for filtering)
-- =============================================================================

-- Variable: bucket_name
-- Query:
SELECT DISTINCT bucket_name AS __text, bucket_name AS __value
FROM projects
WHERE is_active = TRUE
ORDER BY bucket_name;

-- Variable: company_name
-- Query:
SELECT DISTINCT company_name AS __text, company_name AS __value
FROM companies
WHERE is_active = TRUE
ORDER BY company_name;

-- Variable: s3_prefix
-- Query:
SELECT DISTINCT s3_prefix AS __text, s3_prefix AS __value
FROM sync_sessions
ORDER BY s3_prefix;

-- Variable: time_range
-- Type: Interval
-- Options: 1h, 6h, 12h, 24h, 7d, 30d, 90d


-- =============================================================================
-- ALERT QUERIES (for Grafana alerting)
-- =============================================================================

-- Alert: High Failure Rate
-- Condition: Failure rate > 10% in last hour
SELECT
    ROUND(
        (SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END)::numeric /
         NULLIF(COUNT(*), 0) * 100),
        2
    ) AS failure_rate
FROM file_uploads
WHERE uploaded_at >= NOW() - INTERVAL '1 hour';
-- Alert if failure_rate > 10


-- Alert: Stalled Upload Session
-- Condition: Session in_progress but no uploads in last 30 minutes
SELECT
    ss.id,
    p.project_name,
    ss.s3_prefix,
    EXTRACT(EPOCH FROM (NOW() - MAX(fu.uploaded_at))) / 60 AS minutes_since_last_upload
FROM sync_sessions ss
JOIN projects p ON ss.project_id = p.id
LEFT JOIN file_uploads fu ON ss.id = fu.session_id
WHERE ss.status = 'in_progress'
GROUP BY ss.id, p.project_name, ss.s3_prefix
HAVING MAX(fu.uploaded_at) < NOW() - INTERVAL '30 minutes'
   OR MAX(fu.uploaded_at) IS NULL;
-- Alert if any rows returned


-- Alert: No Recent Uploads
-- Condition: No files uploaded in last 24 hours
SELECT
    COUNT(*) AS uploads_last_24h
FROM file_uploads
WHERE status = 'uploaded'
  AND uploaded_at >= NOW() - INTERVAL '24 hours';
-- Alert if uploads_last_24h = 0

-- =============================================================================
-- END OF QUERIES
-- =============================================================================
