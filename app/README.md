# P2P Data Products - Flask Backend

Production-ready Flask REST API for P2P Data Products application.

## Quick Start

**From project root:**

```bash
python server.py
```

Server starts at: http://localhost:5000

## Features

- ✅ HANA Cloud data products API
- ✅ SQL execution engine
- ✅ Connection management
- ✅ SQLite persistent logging (2-day retention)
- ✅ RESTful API design
- ✅ CORS enabled
- ✅ Health check endpoint
- ✅ Error handling

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/data-products` | GET | List data products |
| `/api/data-products/<schema>/tables` | GET | Get tables in schema |
| `/api/data-products/<schema>/<table>/query` | POST | Query table data |
| `/api/execute-sql` | POST | Execute SQL query |
| `/api/logs` | GET | Get application logs |
| `/api/logs/stats` | GET | Get log statistics |
| `/api/logs/clear` | POST | Clear all logs |

## Configuration

Edit `backend/.env`:

```bash
HANA_HOST=your-instance.hana.prod-eu10.hanacloud.ondemand.com
HANA_PORT=443
HANA_USER=your_user
HANA_PASSWORD=your_password
HANA_SCHEMA=P2P_SCHEMA
ENV=development
LOG_RETENTION_DAYS=2
```

## Requirements

```bash
pip install -r backend/requirements.txt
```

## Development

**Run with auto-reload:**
```bash
python server.py
```

**Check health:**
```bash
curl http://localhost:5000/api/health
```

## Architecture

```
backend/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env               # Configuration (not in git)
└── README.md          # This file

logs/                   # Auto-created
└── app_logs.db        # SQLite log database
```

## Version

**v1.1.0** - Flask backend with SQLite logging

## Documentation

See `/docs` for complete documentation.
