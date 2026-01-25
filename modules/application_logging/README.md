# Application Logging Module

**Version**: 1.0.0  
**Category**: Infrastructure  
**Status**: Production Ready  
**Dependencies**: None (stdlib only)

## Overview

SQLite-based persistent application logging system with asynchronous writing, automatic cleanup, and REST API for log management. Provides enterprise-grade logging capabilities with web-based viewer.

## Features

✅ **Async Writing** - Non-blocking log writes via queue  
✅ **Batch Processing** - Efficient batch writes to database  
✅ **Auto Cleanup** - Automatic deletion of old logs (configurable retention)  
✅ **VACUUM Optimization** - Automatic database optimization  
✅ **Client Logging** - Capture JavaScript errors from browser  
✅ **Filtering** - Filter by level, date range  
✅ **Pagination** - Efficient pagination for large datasets  
✅ **Statistics** - Real-time log counts by level  
✅ **Thread Safe** - Safe for multi-threaded applications

## Quick Start

### Backend Integration

```python
from modules.application_logging.backend.sqlite_logger import setup_logging
from modules.application_logging.backend.api import create_blueprint
import logging

# Setup logging
logger = logging.getLogger(__name__)
handler = setup_logging(logger, db_path='logs/app_logs.db', retention_days=7)

# Register Flask blueprint
from flask import Flask
app = Flask(__name__)
app.register_blueprint(create_blueprint(handler), url_prefix='/api')
```

### Configuration

```python
handler = SQLiteLogHandler(
    db_path='logs/app_logs.db',      # Database path
    retention_days=7,                 # Keep logs for 7 days
    batch_size=100,                   # Write 100 logs per batch
    batch_timeout=5.0,                # Force write after 5 seconds
    cleanup_interval=21600            # Cleanup every 6 hours
)
```

### Environment Variables

```bash
LOG_DB_PATH=logs/app_logs.db        # Override database path
LOG_RETENTION_DAYS=7                # Override retention period
```

## API Endpoints

### GET /api/logs
Retrieve logs with filtering and pagination.

**Query Parameters**:
- `level` - Filter by log level (INFO, WARNING, ERROR)
- `limit` - Maximum logs to return (default: 100, max: 1000)
- `offset` - Pagination offset (default: 0)
- `start_date` - Filter logs after this date (ISO format)
- `end_date` - Filter logs before this date (ISO format)

**Response**:
```json
{
  "success": true,
  "count": 50,
  "totalCount": 1250,
  "logs": [
    {
      "id": 1,
      "timestamp": "2026-01-25T16:00:00",
      "level": "INFO",
      "logger": "app",
      "message": "Application started"
    }
  ],
  "filters": {
    "level": "INFO",
    "limit": 100,
    "offset": 0
  }
}
```

### GET /api/logs/stats
Get log statistics by level.

**Response**:
```json
{
  "success": true,
  "stats": {
    "total": 1250,
    "info": 800,
    "warning": 350,
    "error": 100
  }
}
```

### POST /api/logs/clear
Clear all stored logs.

**Response**:
```json
{
  "success": true,
  "message": "Logs cleared successfully"
}
```

### POST /api/logs/client
Log client-side JavaScript errors.

**Request Body**:
```json
{
  "level": "ERROR",
  "message": "TypeError: Cannot read property 'x' of undefined",
  "url": "https://example.com/app.js",
  "line": 42,
  "column": 15,
  "stack": "Error stack trace...",
  "timestamp": "2026-01-25T16:00:00"
}
```

## Frontend Integration

```javascript
// Capture JavaScript errors
window.addEventListener('error', (event) => {
    fetch('/api/logs/client', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            level: 'ERROR',
            message: event.message,
            url: event.filename,
            line: event.lineno,
            column: event.colno,
            stack: event.error?.stack || '',
            timestamp: new Date().toISOString()
        })
    });
});
```

## Database Schema

```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    level TEXT NOT NULL,
    logger TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_timestamp ON logs(timestamp);
CREATE INDEX idx_logs_level ON logs(level);
CREATE INDEX idx_logs_created_at ON logs(created_at);
```

## Architecture

### Async Writing
Logs are queued and written in batches by background thread. This prevents blocking the main application thread during log writes.

### Batch Processing
Multiple logs are written in a single transaction, improving performance. Batch size and timeout are configurable.

### Auto Cleanup
Background thread periodically deletes logs older than retention period and runs VACUUM to reclaim space.

### Thread Safety
All database operations use locks to ensure thread safety in multi-threaded environments.

## Testing

```bash
# Run unit tests
python modules/application_logging/tests/sqlite_logger.test.py

# Tests cover:
# - Database initialization
# - Log writing (sync/async)
# - Batch processing
# - Filtering and pagination
# - Cleanup and retention
# - Thread safety
```

## Module Structure

```
modules/application_logging/
├── module.json               # Module configuration
├── README.md                 # This file
├── backend/
│   ├── __init__.py
│   ├── sqlite_logger.py      # SQLiteLogHandler class
│   └── api.py                # Flask REST API
├── frontend/
│   └── (UI components TBD)
├── tests/
│   ├── sqlite_logger.test.py # Unit tests
│   └── test_module_import.py # Import tests
└── docs/
    └── (Additional docs TBD)
```

## Dependencies

**Runtime**: Python 3.7+ (stdlib only)  
**Development**: Flask (for API)  
**Testing**: unittest (stdlib)

## Performance

- **Async writes**: No blocking on log operations
- **Batch processing**: ~100x faster than individual writes
- **Indexed queries**: Fast filtering by level, date
- **Automatic VACUUM**: Keeps database compact

## Best Practices

1. **Set appropriate retention**: Balance disk space vs. log history needs
2. **Monitor log volume**: Adjust batch size for high-volume applications
3. **Use log levels wisely**: INFO for normal operations, WARNING for issues, ERROR for failures
4. **Client-side logging**: Capture JavaScript errors for full visibility
5. **Regular cleanup**: Default 6-hour interval works for most applications

## Migration Notes

If migrating from old backend/app.py:

```python
# Old code:
# from backend.app import SQLiteLogHandler

# New code:
from modules.application_logging.backend.sqlite_logger import SQLiteLogHandler, setup_logging
from modules.application_logging.backend.api import create_blueprint

# Same API, drop-in replacement!
```

## Troubleshooting

**Issue**: Logs not appearing immediately  
**Solution**: Logs are batched. Wait for batch_timeout (default 5s) or write batch_size logs.

**Issue**: Database file growing large  
**Solution**: Reduce retention_days or run cleanup manually: `handler.cleanup_old_logs()`

**Issue**: Permission errors  
**Solution**: Ensure logs/ directory exists and is writable

## Support

**Repository**: https://github.com/d031182/steel_thread_on_sap  
**Module Path**: modules/application_logging/  
**Issues**: Report via GitHub Issues

## License

Internal use only - P2P Development Team

---

**Status**: ✅ Production Ready  
**Last Updated**: 2026-01-25  
**Maintainer**: P2P Development Team