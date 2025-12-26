# Grafana Queries

SQL queries for creating Grafana dashboards to monitor upload statistics.

## Setup

1. Add PostgreSQL as a data source in Grafana:
   - Host: `localhost:5432` (or your database host)
   - Database: `data_uploader`
   - User: `uploader`
   - Password: `uploader_pass`
   - SSL Mode: `disable` (for local development)

2. Create a new dashboard and add panels with the queries below.

## Queries

### 1. Total Files Per Project (Table)

Shows total files uploaded for each project/bucket.

```sql
SELECT
    p.project_name AS "Project Name",
    p.bucket_name AS "Bucket Name",
    COUNT(DISTINCT fu.id) AS "Total Files",
    ROUND(SUM(fu.file_size)::numeric / (1024^3), 2) AS "Total Size (GB)",
    COUNT(DISTINCT ss.id) AS "Total Sessions"
FROM projects p
LEFT JOIN sync_sessions ss ON p.id = ss.project_id
LEFT JOIN file_uploads fu ON ss.id = fu.session_id AND fu.status = 'uploaded'
GROUP BY p.id, p.project_name, p.bucket_name
ORDER BY p.project_name;
```

**Panel Type:** Table
**Refresh:** On Dashboard Load

---

### 2. Upload Status Per Project (Table)

Shows current upload status for each project.

```sql
SELECT
    p.project_name AS "Project",
    ss.s3_prefix AS "Cycle",
    ss.status AS "Status",
    ss.total_files AS "Total Files",
    ss.files_uploaded AS "Uploaded",
    ss.files_failed AS "Failed",
    ss.files_skipped AS "Skipped",
    ROUND((ss.files_uploaded::numeric / NULLIF(ss.total_files, 0) * 100), 1) AS "Progress %",
    ROUND(ss.total_size_bytes::numeric / (1024^3), 2) AS "Size (GB)",
    ss.started_at AS "Started",
    ss.completed_at AS "Completed"
FROM sync_sessions ss
JOIN projects p ON ss.project_id = p.id
ORDER BY ss.started_at DESC
LIMIT 50;
```

**Panel Type:** Table
**Refresh:** 30s

---

### 3. Files by Type and Cycle (Bar Chart)

Compare quantity of files by type across different cycles for a specific bucket.

```sql
SELECT
    ss.s3_prefix AS "Cycle",
    fu.file_type AS "File Type",
    COUNT(*) AS "Count"
FROM file_uploads fu
JOIN sync_sessions ss ON fu.session_id = ss.id
JOIN projects p ON ss.project_id = p.id
WHERE p.bucket_name = '${bucket_name:text}'
  AND fu.status = 'uploaded'
GROUP BY ss.s3_prefix, fu.file_type
ORDER BY ss.s3_prefix, fu.file_type;
```

**Panel Type:** Bar Chart
**Variables:**
- `bucket_name`: Query: `SELECT DISTINCT bucket_name FROM projects ORDER BY bucket_name`
**X-axis:** Cycle
**Legend:** File Type
**Stacking:** Normal
**Refresh:** On Dashboard Load

---

### 4. Upload Success Rate (Stat Panel)

Shows overall upload success rate.

```sql
SELECT
    ROUND(
        (SUM(CASE WHEN status = 'uploaded' THEN 1 ELSE 0 END)::numeric /
         NULLIF(COUNT(*), 0) * 100),
        2
    ) AS "Success Rate %"
FROM file_uploads;
```

**Panel Type:** Stat
**Unit:** Percent (0-100)
**Thresholds:**
- Red: < 90
- Yellow: 90-95
- Green: > 95
**Refresh:** 30s

---

### 5. Total Uploaded Size Over Time (Time Series)

Shows cumulative uploaded data size over time.

```sql
SELECT
    DATE_TRUNC('day', uploaded_at) AS "time",
    SUM(file_size) / (1024^3) AS "Size (GB)"
FROM file_uploads
WHERE status = 'uploaded'
  AND uploaded_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', uploaded_at)
ORDER BY "time";
```

**Panel Type:** Time Series
**Y-axis:** Size (GB)
**Refresh:** 1m

---

### 6. Active Sessions (Table)

Shows currently active upload sessions.

```sql
SELECT
    ss.id AS "Session ID",
    p.project_name AS "Project",
    ss.s3_prefix AS "Cycle",
    ss.total_files AS "Total Files",
    ss.files_uploaded AS "Uploaded",
    ss.files_failed AS "Failed",
    ROUND((ss.files_uploaded::numeric / NULLIF(ss.total_files, 0) * 100), 1) AS "Progress %",
    EXTRACT(EPOCH FROM (NOW() - ss.started_at)) / 60 AS "Duration (min)",
    ss.started_at AS "Started"
FROM sync_sessions ss
JOIN projects p ON ss.project_id = p.id
WHERE ss.status = 'in_progress'
ORDER BY ss.started_at DESC;
```

**Panel Type:** Table
**Refresh:** 10s

---

### 7. Failed Files Summary (Table)

Shows files that failed to upload with error messages.

```sql
SELECT
    p.project_name AS "Project",
    ss.s3_prefix AS "Cycle",
    fu.local_path AS "File Path",
    fu.file_type AS "Type",
    fu.retry_count AS "Retries",
    fu.error_message AS "Error",
    fu.updated_at AS "Last Attempt"
FROM file_uploads fu
JOIN sync_sessions ss ON fu.session_id = ss.id
JOIN projects p ON ss.project_id = p.id
WHERE fu.status = 'failed'
ORDER BY fu.updated_at DESC
LIMIT 100;
```

**Panel Type:** Table
**Refresh:** 1m

---

### 8. Upload Speed (Gauge)

Shows average upload speed in files per second for recent sessions.

```sql
SELECT
    ROUND(
        AVG(
            ss.files_uploaded::numeric /
            NULLIF(EXTRACT(EPOCH FROM (ss.completed_at - ss.started_at)), 0)
        ),
        2
    ) AS "Files/Second"
FROM sync_sessions ss
WHERE ss.status IN ('completed', 'completed_with_errors')
  AND ss.completed_at >= NOW() - INTERVAL '7 days';
```

**Panel Type:** Gauge
**Unit:** Files/sec
**Min:** 0
**Max:** 10
**Refresh:** 1m

---

### 9. File Type Distribution (Pie Chart)

Shows distribution of file types across all uploads.

```sql
SELECT
    file_type AS "File Type",
    COUNT(*) AS "Count"
FROM file_uploads
WHERE status = 'uploaded'
GROUP BY file_type
ORDER BY COUNT(*) DESC;
```

**Panel Type:** Pie Chart
**Legend:** Bottom
**Refresh:** On Dashboard Load

---

### 10. Daily Upload Statistics (Table)

Shows daily upload statistics for the last 30 days.

```sql
SELECT
    DATE(uploaded_at) AS "Date",
    COUNT(*) AS "Files Uploaded",
    COUNT(DISTINCT session_id) AS "Sessions",
    ROUND(SUM(file_size)::numeric / (1024^3), 2) AS "Total Size (GB)",
    COUNT(DISTINCT file_type) AS "File Types"
FROM file_uploads
WHERE status = 'uploaded'
  AND uploaded_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(uploaded_at)
ORDER BY "Date" DESC;
```

**Panel Type:** Table
**Refresh:** 1h

---

## Dashboard Variables

Create these variables to make dashboards interactive:

### bucket_name
```sql
SELECT DISTINCT bucket_name FROM projects ORDER BY bucket_name;
```

### s3_prefix
```sql
SELECT DISTINCT s3_prefix FROM sync_sessions ORDER BY s3_prefix;
```

### time_range
- Type: Interval
- Options: Last 24 hours, Last 7 days, Last 30 days, Last 90 days

## Alerts

Configure alerts in Grafana for:

1. **High Failure Rate**
   - Condition: Success rate < 90%
   - Alert every: 15 minutes

2. **Long Running Session**
   - Condition: Session in_progress for > 6 hours
   - Alert every: 1 hour

3. **No Uploads in 24h**
   - Condition: No files uploaded in last 24 hours
   - Alert every: 24 hours
