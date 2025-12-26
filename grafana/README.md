# Grafana Dashboard for Data Uploader

This folder contains Grafana dashboard configurations and SQL queries for monitoring upload progress and analytics.

## Quick Start

### 1. Add PostgreSQL Data Source

In Grafana, add a new PostgreSQL data source:

```
Name: Data Uploader DB
Host: localhost:5432
Database: data_uploader
User: uploader
Password: uploader_pass
SSL Mode: disable (for local/development)
```

For production, use appropriate SSL settings and credentials.

### 2. Create Dashboard

You have two options:

#### Option A: Import Dashboard JSON (Recommended)
1. Download `dashboard.json` from this folder
2. In Grafana: Create → Import → Upload JSON file
3. Select the "Data Uploader DB" data source
4. Click Import

#### Option B: Manual Setup
1. Use queries from `queries.sql`
2. Create panels manually following the instructions in each query comment
3. Configure refresh intervals and panel types as documented

## Dashboard Sections

### 📊 Real-Time Monitoring (for CLI uploads)

Perfect for watching active uploads in real-time:

- **Active Upload Sessions** - Table showing all in-progress uploads with live progress
- **Upload Progress Gauge** - Visual gauge for current upload completion %
- **Current Upload Speed** - Real-time files/second metric
- **Files Uploaded Today** - Counter for daily progress
- **Recent Session Timeline** - Bar gauge showing progress of last 10 sessions

**Recommended Refresh:** 5-10 seconds

### 📈 Statistics & Analytics

For historical analysis and reporting:

- **Total Files Per Project** - Summary table of all projects
- **Files by Cycle Comparison** - Bar chart comparing cycles
- **Upload Success Rate Over Time** - Time series trend
- **File Type Distribution** - Pie chart of file types
- **Session History** - Complete upload history table
- **Upload Volume Over Time** - Area chart showing daily trends
- **Average Upload Speed by Project** - Performance comparison

**Recommended Refresh:** 1 minute - 1 hour (depending on panel)

### 🚨 Troubleshooting

Panels to identify and diagnose issues:

- **Failed Files Report** - Detailed error messages
- **Stalled Sessions** - Sessions with no progress
- **High Failure Rate Alert** - Automatic alerting when failures spike

## Dashboard Variables

Interactive filters to customize views:

| Variable | Purpose | Query |
|----------|---------|-------|
| `bucket_name` | Filter by S3 bucket | All active project buckets |
| `company_name` | Filter by company | All active companies |
| `s3_prefix` | Filter by cycle | All cycle prefixes |
| `time_range` | Time window | 1h, 6h, 12h, 24h, 7d, 30d, 90d |

## Panel Configuration Examples

### Active Upload Sessions Table

```
Query: See queries.sql - Query #1
Panel Type: Table
Refresh: 5s
Width: Full width
Height: 300px
```

### Upload Progress Gauge

```
Query: See queries.sql - Query #2
Panel Type: Gauge
Refresh: 5s
Min: 0
Max: 100
Thresholds:
  - Red: 0-30
  - Yellow: 30-70
  - Green: 70-100
```

### Files by Cycle (Bar Chart)

```
Query: See queries.sql - Query #7
Panel Type: Bar Chart (Grouped)
X-axis: Cycle
Legend: File Type
Stacking: None (for grouped view)
```

## Alerts

Configure Grafana alerts for proactive monitoring:

### 1. High Failure Rate

```yaml
Alert Name: High Upload Failure Rate
Query: See queries.sql - Alert query #1
Condition: failure_rate > 10
Evaluate: Every 5 minutes
For: 10 minutes
Notification: Email/Slack
Message: Upload failure rate is above 10% - investigate immediately
```

### 2. Stalled Upload Session

```yaml
Alert Name: Stalled Upload
Query: See queries.sql - Alert query #2
Condition: Rows > 0
Evaluate: Every 5 minutes
For: 15 minutes
Notification: Email/Slack
Message: Upload session appears stalled - no files uploaded in 30 minutes
```

### 3. No Recent Uploads

```yaml
Alert Name: No Uploads in 24h
Query: See queries.sql - Alert query #3
Condition: uploads_last_24h = 0
Evaluate: Every 1 hour
For: 24 hours
Notification: Email
Message: No files uploaded in the last 24 hours - check system status
```

## Customization

### Adding Custom Queries

1. Open `queries.sql`
2. Add your query with comments following the existing format
3. Create a new panel in Grafana
4. Copy the query
5. Configure panel settings

### Modifying Refresh Intervals

For real-time monitoring:
- Active sessions: 5-10 seconds
- Current stats: 30 seconds

For analytics:
- Historical charts: 1-5 minutes
- Summary tables: On dashboard load

Adjust based on your system load and monitoring needs.

### Color Schemes

Suggested color schemes for consistency:

**Success/Progress:**
- Green: #73BF69 (success, > 90%)
- Yellow: #F2CC0C (warning, 50-90%)
- Red: #E02F44 (error, < 50%)

**File Types:**
- WAV (audio): #1F77B4 (blue)
- JPG (images): #FF7F0E (orange)
- MP4 (video): #2CA02C (green)

## Performance Tips

1. **Use time ranges** - Don't query all historical data
2. **Limit row counts** - Use LIMIT in queries (already included)
3. **Index database** - Ensure proper indexes on `uploaded_at`, `status`, `session_id`
4. **Adjust refresh** - Longer intervals for historical data, shorter for real-time

## Grafana Optimization

### Recommended Settings

```
Dashboard Settings:
  - Timezone: Browser time
  - Auto-refresh: Off (use panel-specific refresh)
  - Time range: Last 24 hours (default)

Panel Settings:
  - Cache timeout: 60 (for heavy queries)
  - Query timeout: 30s
  - Max data points: 1000
```

### Database Indexes

Ensure these indexes exist for optimal performance:

```sql
-- Already created by migrations, but verify:
CREATE INDEX IF NOT EXISTS idx_file_uploads_status ON file_uploads(status);
CREATE INDEX IF NOT EXISTS idx_file_uploads_uploaded_at ON file_uploads(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_file_uploads_session_id ON file_uploads(session_id);
CREATE INDEX IF NOT EXISTS idx_sync_sessions_status ON sync_sessions(status);
CREATE INDEX IF NOT EXISTS idx_sync_sessions_started_at ON sync_sessions(started_at);
```

## Troubleshooting

### Dashboard not loading

1. Verify PostgreSQL data source is configured correctly
2. Test connection in Data Sources settings
3. Check database credentials in `.env`

### Queries returning no data

1. Verify data exists: `SELECT COUNT(*) FROM sync_sessions;`
2. Check time range filters
3. Ensure dashboard variables are set correctly

### Slow query performance

1. Add/verify database indexes (see above)
2. Reduce time ranges
3. Increase query cache timeout
4. Use EXPLAIN on slow queries

## Example Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│                     UPLOAD MONITORING                        │
├──────────────┬──────────────┬──────────────┬────────────────┤
│ Files Today  │ Success Rate │ Active       │ Current Speed  │
│   [STAT]     │   [GAUGE]    │ Sessions     │   [STAT]       │
│              │              │   [STAT]     │                │
├──────────────┴──────────────┴──────────────┴────────────────┤
│                                                              │
│         Active Upload Sessions (Table)                       │
│   [Live progress of current uploads - 5s refresh]           │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│    Upload Progress Over Time (Time Series)                   │
│                                                              │
├─────────────────────┬────────────────────────────────────────┤
│                     │                                        │
│  File Type Dist.    │  Files by Cycle (Bar Chart)           │
│   (Pie Chart)       │                                        │
│                     │                                        │
├─────────────────────┴────────────────────────────────────────┤
│                                                              │
│              Session History (Table)                         │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│              Failed Files Report (Table)                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Support

- 📖 See `queries.sql` for all query definitions
- 📚 Full documentation: [../doc/reference/GRAFANA_QUERIES.md](../doc/reference/GRAFANA_QUERIES.md)
- 🐛 Report issues: GitHub Issues

---

**Last Updated:** December 26, 2025
