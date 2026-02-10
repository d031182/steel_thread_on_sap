"""
HANA Connection Module
=====================
SAP HANA Cloud connection management with credential storage.

Quick Start:
    from modules.hana_connection.frontend.hanaConnectionAPI import HanaConnectionAPI
    
    # Create API instance
    api = HanaConnectionAPI()
    
    # Save connection
    await api.saveConnection('production', {
        'host': 'your-instance.hanacloud.ondemand.com',
        'port': 443,
        'user': 'your_user',
        'password': 'your_password'
    })
    
    # Test connection
    result = await api.testConnection('production')
    if result.success:
        print('Connected!')
    
    # Get connection
    conn = await api.getConnection('production')
    
    # Check health
    health = await api.getHealthStatus('production')

Features:
- Save and load HANA connection details
- Secure credential storage (localStorage)
- Test connections before saving
- Monitor connection health
- Support multiple instances
- Connection parameter validation
- Comprehensive error handling

Use Cases:
- Store HANA Cloud credentials
- Manage multiple HANA instances  
- Test connections before use
- Monitor database health
- Build database UIs
- Enterprise connectivity

Security:
- Credentials stored in localStorage
- Use HTTPS in production
- Consider backend storage for sensitive environments
- Implement credential rotation
- Use environment variables when possible

Author: P2P Development Team
Version: 1.0.0
"""

__version__ = '1.0.0'