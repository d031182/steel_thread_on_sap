# Login Manager Module

**Version**: 1.0.0  
**Category**: Infrastructure  
**Status**: Complete

## Overview

The Login Manager module provides user authentication and session management for the P2P Data Products application. It supports auto-login with a default user (HANA_DP_USER) for development convenience, while maintaining the flexibility for manual authentication.

## Features

- ✅ **Auto-Login**: Automatically logs in with HANA_DP_USER on first access
- ✅ **Session Management**: Flask session-based user tracking
- ✅ **Multiple Users**: Supports HANA_DP_USER and DBADMIN
- ✅ **Role-Based Access**: data_viewer vs admin roles
- ✅ **Stateless API**: RESTful endpoints for authentication

## Architecture

### Components

1. **AuthenticationService** (`auth_service.py`)
   - Core authentication logic
   - Validates credentials against environment variables
   - Returns User objects

2. **SessionManager** (`session_manager.py`)
   - Manages Flask sessions
   - Auto-initializes with default user
   - Provides get_current_user() helper

3. **REST API** (`api.py`)
   - `/api/login-manager/current-user` - Get logged-in user
   - `/api/login-manager/login` - Manual login
   - `/api/login-manager/logout` - Logout (reverts to auto-login)
   - `/api/login-manager/validate` - Validate session

## Integration

### Step 1: Register Blueprint in app.py

Add this to your `app/app.py` where other modules are registered:

```python
module_loader.load_blueprint(
    "Login Manager",
    "modules.login_manager.backend",
    "login_manager_api",
    "/api/login-manager",
    is_critical=True  # Essential for user authentication
)
```

### Step 2: Configure Flask Secret Key

Add to `app/app.py` before creating the Flask app:

```python
# Configure session secret key for login_manager
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
```

### Step 3: Use in Your Code

## Usage

### Backend (Python)

```python
from modules.login_manager.backend import get_current_user

def my_function():
    # Get current authenticated user
    user = get_current_user()
    print(f"Current user: {user.username}")
    print(f"Role: {user.role}")
```

### Frontend (JavaScript)

```javascript
// Get current user
const response = await fetch('/api/login-manager/current-user');
const data = await response.json();
console.log('Logged in as:', data.user.username);

// Manual login (if needed)
const loginResponse = await fetch('/api/login-manager/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        username: 'DBADMIN',
        password: 'password'
    })
});
```

## Configuration

In `app/.env`:

```bash
# Active User (for application runtime)
HANA_USER=HANA_DP_USER
HANA_PASSWORD=YourSecurePassword123!

# Admin User (for administrative tasks)
HANA_ADMIN_USER=DBADMIN
HANA_ADMIN_PASSWORD=HANA4vpbdc!SYS
```

## Default Behavior

1. **First Request**: No session exists
   - Auto-login with HANA_DP_USER
   - Role: data_viewer
   - Source: auto

2. **Subsequent Requests**: Session exists
   - Returns cached user from session
   - No re-authentication needed

3. **Manual Login**: User provides credentials
   - Validates against .env variables
   - Updates session with new user
   - Source: manual

4. **Logout**: User clicks logout
   - Clears manual session
   - Reverts to auto-login (HANA_DP_USER)

## Integration with Data Sources

Data sources should query login_manager instead of reading .env directly:

```python
# OLD (hardwired):
hana_user = os.getenv('HANA_USER')

# NEW (uses authenticated user):
from modules.login_manager.backend import get_current_user
user = get_current_user()
hana_user = user.username
```

## User Roles

| Role | Username | Privileges |
|------|----------|------------|
| data_viewer | HANA_DP_USER | Read data products |
| admin | DBADMIN | Full database admin |

## Security

- ✅ Passwords never exposed via API
- ✅ Session-based authentication
- ✅ Default user for development convenience
- ✅ Manual login for production scenarios
- ✅ Role-based access control ready

## Testing

Run module tests:
```bash
python -m pytest modules/login_manager/tests/ -v
```

## Quality Gate

```bash
python core/quality/module_quality_gate.py login_manager
```

## Dependencies

- Flask (session management)
- Python 3.8+ (typing support)

## Future Enhancements

- [ ] LDAP integration
- [ ] OAuth2 support
- [ ] Multi-factor authentication
- [ ] User management UI
- [ ] Password reset flow
- [ ] Session timeout handling

## Related Modules

- [[HANA Connection]] - Uses authenticated user
- [[SQLite Connection]] - Uses authenticated user
- [[Data Products]] - Queries for current user

---

**Status**: ✅ Module complete and ready for integration