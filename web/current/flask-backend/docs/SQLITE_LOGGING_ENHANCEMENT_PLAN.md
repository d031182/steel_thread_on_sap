# SQLite Logging Enhancement Plan

**Feature**: Persistent Application Logging with SQLite  
**Version**: 3.3  
**Date**: January 22, 2026  
**Status**: Planning → Implementation

---

## 🎯 Objective

Replace in-memory logging with persistent SQLite database storage to:
- Retain logs across server restarts
- Enable historical log analysis
- Automatic cleanup of old logs (2-day retention)
- Better query/filter capabilities
- Production-grade logging solution

---

## 📋 Requirements

### Functional Requirements
1. Store all application logs in SQLite database
2. Automatically delete logs older than 2 days
3. Maintain existing log viewing API endpoints
4. Support log filtering by level, date, logger
5. Preserve log format and metadata

### Non-Functional Requirements
1. Minimal performance impact (async writes)
2. Automatic database initialization
3. Thread-safe operations
4. Database file: `flask-backend/logs/app_logs.db`
5. Max database size: 100 MB (with auto-cleanup)

---

## 🏗️ Architecture Design

### Database Schema

```sql
CREATE TABLE application_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(10) NOT NULL,
    logger VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    created_at DATETIME NOT NULL
);

CREATE INDEX idx_timestamp ON application_logs(timestamp);
CREATE INDEX idx_level ON application_logs(level);
CREATE INDEX idx_created_at ON application_logs(created_at);
```

### Components

**1. SQLiteLogHandler (logging.Handler)**
- Custom Python logging handler
- Writes logs to SQLite asynchronously
- Batch inserts for performance
- Thread-safe with queue

**2. LogCleanupService**
- Background task
- Runs every 6 hours
- Deletes logs older than 2 days
- Vacuum database if needed

**3. Updated API Endpoints**
- `/api/logs` - Query from SQLite
- `/api/logs/clear` - Clear all logs
- `/api/logs/stats` - Log statistics

---

## 🔄 Migration Path

### Before (In-Memory)
```python
class MemoryLogHandler(logging.Handler):
    def __init__(self, max_logs=100):
        self.logs = []  # Lost on restart!
```

### After (SQLite)
```python
class SQLiteLogHandler(logging.Handler):
    def __init__(self, db_path, retention_days=2):
        self.db_path = db_path
        self.retention_days = retention_days
        self.init_database()
```

---

## 📝 Implementation Phases

### Phase 1: Database Setup (30 minutes)
- [x] Create logs directory
- [ ] Create SQLite schema
- [ ] Add database initialization
- [ ] Test database creation

### Phase 2: SQLiteLogHandler (45 minutes)
- [ ] Implement custom handler class
- [ ] Add async log writing with queue
- [ ] Thread safety with locks
- [ ] Error handling for DB failures
- [ ] Test handler with various log levels

### Phase 3: Cleanup Service (30 minutes)
- [ ] Implement background cleanup task
- [ ] Configure 2-day retention
- [ ] Add vacuum operation
- [ ] Schedule cleanup every 6 hours
- [ ] Test cleanup logic

### Phase 4: API Updates (30 minutes)
- [ ] Update `/api/logs` to query SQLite
- [ ] Support pagination (limit/offset)
- [ ] Add date range filtering
- [ ] Add log statistics endpoint
- [ ] Update `/api/logs/clear`

### Phase 5: Testing (30 minutes)
- [ ] Test log writing
- [ ] Test log retrieval
- [ ] Test cleanup after 2 days
- [ ] Test concurrent access
- [ ] Verify no memory leaks

### Phase 6: Documentation (15 minutes)
- [ ] Update API documentation
- [ ] Add configuration guide
- [ ] Document database schema
- [ ] Update PROJECT_TRACKER

**Total Estimated Time**: 3 hours

---

## 🔧 Configuration

### Environment Variables
```bash
# .env
LOG_DB_PATH=logs/app_logs.db
LOG_RETENTION_DAYS=2
LOG_CLEANUP_INTERVAL=21600  # 6 hours in seconds
LOG_MAX_DB_SIZE_MB=100
```

### Database Location
```
web/current/flask-backend/
├── logs/
│   ├── app_logs.db        # SQLite database
│   └── .gitignore         # Ignore DB file
```

---

## 🧪 Testing Strategy

### Unit Tests
```python
def test_sqlite_handler_writes_logs():
    handler = SQLiteLogHandler(":memory:")
    logger.addHandler(handler)
    logger.info("Test message")
    # Verify log in database

def test_cleanup_deletes_old_logs():
    # Insert logs with old timestamps
    cleanup_service.run()
    # Verify old logs deleted

def test_concurrent_log_writes():
    # Multiple threads writing logs
    # Verify all logs persisted
```

### Integration Tests
- Restart server and verify logs persist
- Generate 1000 logs and verify performance
- Wait 2 days and verify automatic cleanup

---

## 📊 Performance Considerations

### Write Performance
- Batch inserts (every 100 logs or 5 seconds)
- Async writes with queue
- No blocking on main thread

### Read Performance
- Indexed queries (timestamp, level)
- Pagination support
- Limit result sets (max 1000 logs)

### Storage Management
- Auto-cleanup every 6 hours
- 2-day retention = ~50,000 logs
- Estimated DB size: 10-20 MB
- Vacuum when DB > 50 MB

---

## 🔒 Security Considerations

1. **SQL Injection**: Use parameterized queries
2. **File Permissions**: Restrict DB file access
3. **Log Content**: Sanitize sensitive data
4. **Database Location**: Inside flask-backend directory

---

## 📈 Benefits

**Persistence**:
- ✅ Logs survive server restarts
- ✅ Historical analysis possible
- ✅ Production debugging easier

**Management**:
- ✅ Automatic cleanup (no manual intervention)
- ✅ Configurable retention (2 days default)
- ✅ Database size controlled

**Query Capabilities**:
- ✅ Complex filtering (date ranges, levels)
- ✅ Pagination for large result sets
- ✅ Statistics and aggregations
- ✅ Export to CSV possible

**Production Ready**:
- ✅ Thread-safe
- ✅ Async writes (no blocking)
- ✅ Error recovery
- ✅ Resource limits enforced

---

## 🚀 Success Criteria

- [x] Planning document created
- [ ] SQLite database created automatically
- [ ] All logs persisted to database
- [ ] Logs older than 2 days deleted automatically
- [ ] API endpoints return data from SQLite
- [ ] No performance degradation
- [ ] Server restarts preserve logs
- [ ] Documentation complete
- [ ] User acceptance

---

## 📚 References

- Python logging: https://docs.python.org/3/library/logging.html
- SQLite Python: https://docs.python.org/3/library/sqlite3.html
- Flask logging: https://flask.palletsprojects.com/en/2.3.x/logging/
- Background tasks: APScheduler or threading

---

*Plan Created*: January 22, 2026, 11:03 AM  
*Estimated Time*: 3 hours  
*Priority*: High (User-requested enhancement)
