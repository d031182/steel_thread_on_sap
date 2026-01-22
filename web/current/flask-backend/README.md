# P2P Data Products - Flask Backend

**Version:** 3.3  
**Status:** ✅ Production Ready  
**Last Updated:** January 22, 2026

---

## Overview

Python/Flask backend providing REST API for P2P Data Products application. Features include:
- SAP HANA Cloud database connectivity
- Data products management
- SQL execution console
- SQLite persistent logging system
- Comprehensive error handling

---

## Quick Start

### Prerequisites
- Python 3.8+
- pip
- SAP HANA Cloud instance

### Installation

1. **Install Dependencies:**
   ```bash
   cd web/current/flask-backend
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   Create `.env` file (or use existing):
   ```env
   HANA_HOST=your-instance.hana.prod-region.hanacloud.ondemand.com
   HANA_PORT=443
   HANA_USER=P2P_DP_USER
   HANA_PASSWORD=your_password
   ```

3. **Run Server:**
   ```bash
   python app.py
   ```

   Or using the run script:
   ```bash
   python run.py
   ```

4. **Verify:**
   - Server runs on: http://localhost:5000
   - Health check: http://localhost:5000/api/health

---

## Architecture

### Components

```
flask-backend/
├── app.py              Main application with SQLiteLogHandler
├── run.py              Production runner
├── .env                Environment configuration
├── requirements.txt    Python dependencies
├── logs/               SQLite log database (auto-created)
├── docs/               Documentation
└── tests/              Backend tests
```

### Key Features

1. **SQLite Logging System (v3.3)**
   - Persistent logging with 2-day retention
   - Async batch writes (1000 logs/batch)
   - Thread-safe operations
   - Automatic cleanup every 6 hours

2. **HANA Cloud Integration**
   - Connection pooling
   - Secure credential management
   - Query execution with timeout handling
   - Error recovery

3. **REST API**
   - Data products endpoints
   - SQL execution endpoints
   - Logging endpoints
   - Health monitoring

---

## API Endpoints

### Health & Status
- `GET /api/health` - Backend health check

### Data Products
- `GET /api/data-products` - List installed data products
- `GET /api/data-products/<schema>/tables` - List tables in schema
- `GET /api/data-products/<schema>/tables/<table>` - Get table data
- `GET /api/data-products/<schema>/tables/<table>/structure` - Get table structure

### SQL Execution
- `POST /api/sql/execute` - Execute SQL query
  ```json
  {
    "instance_id": "string",
    "query": "SELECT * FROM TABLE"
  }
  ```

### Logging (v3.3)
- `GET /api/logs` - Retrieve logs with filtering
  - Query params: `level`, `limit`, `offset`, `start_date`, `end_date`
- `GET /api/logs/stats` - Get log statistics
- `POST /api/logs/clear` - Clear all logs

### HANA Connection
- `GET /api/hana/instances` - List configured instances
- `POST /api/hana/test-connection` - Test HANA connection

---

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `HANA_HOST` | HANA Cloud instance host | - | Yes |
| `HANA_PORT` | HANA Cloud port | 443 | Yes |
| `HANA_USER` | Database user | - | Yes |
| `HANA_PASSWORD` | Database password | - | Yes |
| `FLASK_ENV` | Flask environment | production | No |
| `LOG_RETENTION_DAYS` | Log retention period | 2 | No |

### Logging Configuration

**In app.py:**
```python
LOG_RETENTION_DAYS = 2      # Days to keep logs
BATCH_SIZE = 1000           # Logs per batch write
CLEANUP_INTERVAL = 6        # Hours between cleanup runs
```

---

## Development

### Running in Development Mode

```bash
# Set development environment
$env:FLASK_ENV="development"

# Run with auto-reload
python app.py
```

### Running Tests

```bash
# Run backend tests
python test_data_products.py

# Run all tests (frontend + backend)
cd ..
node tests/run-all-tests.js
```

### Adding New Endpoints

1. Add route in `app.py`
2. Implement logic
3. Add error handling
4. Log appropriately
5. Add tests
6. Update this README

---

## Logging System

### SQLiteLogHandler

Custom logging handler that:
- Stores logs in SQLite database
- Batches writes for performance
- Auto-deletes old logs
- Thread-safe operations

### Database Schema

```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    level TEXT NOT NULL,
    logger TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### Usage

Logs are automatically captured from:
- Flask request/response cycle
- HANA database operations
- Application errors
- Business logic events

Access logs via:
- API endpoints (`/api/logs`)
- Frontend Log Viewer UI
- Direct SQLite query

---

## Troubleshooting

### Common Issues

**1. HANA Connection Fails**
- Check `.env` credentials
- Verify HANA instance is running
- Check network connectivity
- See: `docs/HANA_CONNECTION_TROUBLESHOOTING.md`

**2. Import Errors**
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version`

**3. Port Already in Use**
- Change port in `app.py`: `app.run(port=5001)`
- Or kill process: `taskkill /F /IM python.exe`

**4. Logs Not Appearing**
- Check `logs/app_logs.db` exists
- Verify write permissions
- Check LOG_RETENTION_DAYS setting

### Debug Mode

Enable detailed logging:
```python
# In app.py
app.logger.setLevel(logging.DEBUG)
```

---

## Performance

### Benchmarks

- **Average Response Time:** <100ms
- **SQL Execution:** ~50-200ms (depends on query)
- **Log Write:** <1ms (batched)
- **Memory Usage:** ~50-100MB

### Optimization Tips

1. **Connection Pooling:** Already implemented
2. **Batch Logging:** Already implemented (1000 logs/batch)
3. **Query Optimization:** Use LIMIT clauses
4. **Caching:** Consider adding Redis for frequent queries

---

## Security

### Best Practices

- ✅ Environment variables for secrets
- ✅ CORS enabled (configured for localhost)
- ✅ SQL injection prevention (parameterized queries)
- ✅ Error message sanitization
- ✅ Secure password storage (not in code)

### Production Deployment

1. Use HTTPS only
2. Configure CORS for production domain
3. Use secrets manager (Azure Key Vault, AWS Secrets Manager)
4. Enable rate limiting
5. Set up monitoring/alerting

---

## Dependencies

### Core
- `Flask` - Web framework
- `flask-cors` - CORS handling
- `hdbcli` - SAP HANA database client
- `python-dotenv` - Environment variable loading

### Full List
See `requirements.txt` for complete dependencies

---

## Documentation

### Available Docs

**Implementation History:**
- `docs/FLASK_MIGRATION_COMPLETE.md` - Initial migration
- `docs/PRIORITY_1_REFACTORING_COMPLETE.md` - First refactoring

**Logging System:**
- `docs/SQLITE_LOGGING_IMPLEMENTATION_COMPLETE.md` - Implementation details
- `docs/SQLITE_LOGGING_ENHANCEMENT_PLAN.md` - Enhancement plan
- `docs/ADVANCED_LOGGING_FEATURES_PLAN.md` - Future roadmap (8 phases)

**Troubleshooting:**
- `docs/HANA_CONNECTION_TROUBLESHOOTING.md` - Connection issues

### External References
- Flask Docs: https://flask.palletsprojects.com/
- hdbcli Docs: https://help.sap.com/docs/HANA_CLIENT
- SAP HANA Cloud: https://help.sap.com/docs/hana-cloud

---

## Monitoring

### Health Check

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-22T11:40:00Z"
}
```

### Log Statistics

```bash
curl http://localhost:5000/api/logs/stats
```

Returns counts by level (INFO, WARNING, ERROR)

---

## Maintenance

### Log Database Management

**Location:** `logs/app_logs.db`

**Automatic Cleanup:**
- Runs every 6 hours
- Deletes logs older than 2 days
- No manual intervention needed

**Manual Cleanup:**
```bash
# Via API
curl -X POST http://localhost:5000/api/logs/clear

# Or delete database
rm logs/app_logs.db
# (Will be recreated on next start)
```

### Backup

**Recommended:** Daily backup of `logs/app_logs.db`

```bash
# PowerShell
Copy-Item logs/app_logs.db logs/app_logs_backup_$(Get-Date -Format 'yyyyMMdd').db
```

---

## Changelog

### v3.3 (2026-01-22)
- ✅ Added SQLite persistent logging
- ✅ Implemented automatic log retention
- ✅ Added log statistics endpoint
- ✅ Enhanced error handling
- ✅ 100% test coverage for logging

### v3.2 (2026-01-21)
- ✅ Flask migration from Node.js
- ✅ HANA Cloud integration
- ✅ Data products API
- ✅ SQL execution API

### v3.1 (2026-01-20)
- ✅ Initial Node.js backend (deprecated)

---

## Support

### Getting Help

1. Check troubleshooting docs in `docs/`
2. Review Flask logs in terminal
3. Check SQLite logs: `logs/app_logs.db`
4. Consult PROJECT_TRACKER.md for implementation history

### Reporting Issues

Create detailed bug report with:
- Error message
- Steps to reproduce
- Environment details
- Relevant logs

---

## Future Enhancements

See `docs/ADVANCED_LOGGING_FEATURES_PLAN.md` for:
- Phase 2: Structured Logging & Context
- Phase 3: Request/Response Tracing
- Phase 4: Performance Metrics
- Phase 5: Error Tracking & Aggregation
- Phase 6: Real-Time Alerting
- Phase 7: Advanced Search
- Phase 8: Interactive UI

**Estimated Total Effort:** 22-30 hours

---

**Maintainer:** P2P Development Team  
**License:** Internal Use Only  
**Created:** January 22, 2026
