# P2P Data Products Backend API

Node.js backend server providing real SAP HANA Cloud database connectivity for the P2P Data Products application.

## Features

- ✅ **Real HANA Cloud Execution** - Uses @sap/hana-client for authentic database queries
- ✅ **RESTful API** - Clean endpoints for SQL execution
- ✅ **Error Handling** - Comprehensive error messages and suggestions
- ✅ **CORS Enabled** - Frontend can call from different ports
- ✅ **Environment Config** - Secure credential management
- ✅ **BTP Ready** - Designed for Cloud Foundry deployment

## Prerequisites

- Node.js 14+ installed
- SAP HANA Cloud instance running
- Database credentials (user, password, host)
- Network access to HANA Cloud (check IP allowlist in BTP)

## Quick Start

### 1. Install Dependencies

```bash
cd web/current/backend
npm install
```

This installs:
- `express` - Web framework
- `@sap/hana-client` - HANA database driver
- `dotenv` - Environment variable management
- `cors` - Cross-origin resource sharing

### 2. Configure Environment

Create `.env` file from template:

```bash
cp .env.example .env
```

Edit `.env` with your HANA Cloud credentials:

```env
HANA_HOST=your-instance-id.hana.prod-eu10.hanacloud.ondemand.com
HANA_PORT=443
HANA_USER=P2P_DEV_USER
HANA_PASSWORD=your-actual-password
HANA_SCHEMA=P2P_DATA_PRODUCTS
PORT=3000
```

### 3. Test Connection

```bash
npm test
```

Expected output:
```
✅ Connected to HANA Cloud!
✅ Query executed successfully!
Results: {
  "CURRENT_USER": "P2P_DEV_USER",
  "CURRENT_SCHEMA": "P2P_DATA_PRODUCTS",
  "CURRENT_TIMESTAMP": "2026-01-22 02:00:00.000"
}
🎉 Connection test PASSED!
```

### 4. Start Server

```bash
npm start
```

Server starts on http://localhost:3000

## API Endpoints

### Health Check
```
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-22T02:00:00.000Z",
  "uptime": 123.456,
  "version": "1.0.0"
}
```

### Test Connection
```
GET /api/test-connection
```

Tests HANA Cloud connectivity.

Response:
```json
{
  "success": true,
  "message": "Connection successful",
  "data": {
    "CURRENT_USER": "P2P_DEV_USER",
    "CURRENT_SCHEMA": "P2P_DATA_PRODUCTS"
  }
}
```

### Execute SQL
```
POST /api/execute-sql
Content-Type: application/json

{
  "sql": "SELECT * FROM SYS.USERS WHERE USER_NAME = 'P2P_DEV_USER'",
  "maxRows": 100
}
```

Response (Success):
```json
{
  "success": true,
  "queryType": "SELECT",
  "rowCount": 1,
  "columns": [
    { "name": "USER_NAME", "type": "VARCHAR" },
    { "name": "CREATOR", "type": "VARCHAR" },
    { "name": "CREATE_TIME", "type": "VARCHAR" }
  ],
  "rows": [
    {
      "USER_NAME": "P2P_DEV_USER",
      "CREATOR": "DBADMIN",
      "CREATE_TIME": "2026-01-21 20:00:00.0"
    }
  ],
  "executionTime": 145,
  "timestamp": "2026-01-22T02:00:00.000Z"
}
```

Response (Error):
```json
{
  "success": false,
  "queryType": "SELECT",
  "error": {
    "code": "EXECUTION_ERROR",
    "message": "invalid table name: INVALID_TABLE",
    "details": null
  },
  "executionTime": 50,
  "timestamp": "2026-01-22T02:00:00.000Z"
}
```

### Get Instance Info
```
GET /api/instance-info
```

Returns HANA database version and usage information.

## Frontend Integration

Update `web/current/js/api/sqlExecutionAPI.js`:

```javascript
// Replace _executeQuerySimulated with:
async _executeQueryReal(instance, sql, options) {
    const response = await fetch('http://localhost:3000/api/execute-sql', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            sql,
            maxRows: options.maxRows || 100
        })
    });
    
    const result = await response.json();
    return result;
}
```

Then update the `executeQuery` method to call `_executeQueryReal` instead of `_executeQuerySimulated`.

## Development

### Run with Auto-Restart
```bash
npm run dev
```

Uses `nodemon` to restart server on file changes.

### Project Structure
```
backend/
├── server.js              # Main Express server
├── test-connection.js     # Connection test script
├── package.json           # Dependencies
├── .env.example           # Environment template
├── .env                   # Your credentials (not in git)
└── README.md              # This file
```

## Deployment to BTP Cloud Foundry

### 1. Create manifest.yml
```yaml
---
applications:
- name: p2p-backend
  memory: 256M
  buildpack: nodejs_buildpack
  command: node server.js
  services:
    - my-hana-instance
  env:
    NODE_ENV: production
```

### 2. Deploy
```bash
cf login
cf push
```

The backend will automatically use VCAP_SERVICES for HANA credentials in BTP.

## Troubleshooting

### Connection Failed

**Error**: `Failed to connect to HANA Cloud`

**Solutions**:
1. Check HANA instance is running in BTP Cockpit
2. Verify IP allowlist includes your IP
3. Test credentials with `hana-cli`
4. Ensure .env file exists with correct values

### Query Failed

**Error**: `invalid table name`

**Solutions**:
1. Check table exists: `SELECT * FROM TABLES WHERE SCHEMA_NAME = 'P2P_DATA_PRODUCTS'`
2. Verify schema name in .env
3. Grant SELECT privileges to user

### Port Already in Use

**Error**: `EADDRINUSE: address already in use :::3000`

**Solutions**:
1. Change PORT in .env
2. Kill existing process: `taskkill /F /IM node.exe` (Windows)
3. Or: `lsof -ti:3000 | xargs kill` (Linux/Mac)

## Security Notes

⚠️ **Important**:
- Never commit `.env` file (add to .gitignore)
- Use strong passwords for HANA users
- Enable `sslValidateCertificate: true` in production
- Add authentication middleware for production
- Validate and sanitize SQL inputs
- Implement rate limiting for API endpoints

## Performance Tips

1. **Connection Pooling** - Use `hana.createPool()` for production
2. **Query Limits** - Always use `maxRows` parameter
3. **Indexing** - Ensure proper indexes in HANA
4. **Caching** - Cache frequently accessed data
5. **Monitoring** - Use BTP monitoring tools

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure .env
3. ✅ Test connection
4. ✅ Start server
5. 📋 Update frontend API calls
6. 📋 Test with real queries
7. 📋 Deploy to BTP

## Support

For issues, check:
- [SAP HANA Client Documentation](https://help.sap.com/docs/SAP_HANA_CLIENT)
- [Express.js Documentation](https://expressjs.com/)
- [@sap/hana-client npm](https://www.npmjs.com/package/@sap/hana-client)

## License

Proprietary - Internal SAP Use Only
