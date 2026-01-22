/**
 * HANA Connection Test Script
 * 
 * Tests connectivity to SAP HANA Cloud database.
 * Run with: node test-connection.js
 */

const hana = require('@sap/hana-client');
require('dotenv').config();

// HANA Configuration
const config = {
    host: process.env.HANA_HOST,
    port: process.env.HANA_PORT || 443,
    user: process.env.HANA_USER,
    password: process.env.HANA_PASSWORD,
    currentSchema: process.env.HANA_SCHEMA || '',
    encrypt: true,
    sslValidateCertificate: false
};

console.log('\n🔍 Testing HANA Cloud Connection...\n');
console.log('Configuration:');
console.log(`  Host: ${config.host}`);
console.log(`  Port: ${config.port}`);
console.log(`  User: ${config.user}`);
console.log(`  Schema: ${config.currentSchema || '(default)'}\n`);

const connection = hana.createConnection();

connection.connect(config, (err) => {
    if (err) {
        console.error('❌ Connection FAILED\n');
        console.error('Error:', err.message);
        console.error('\nTroubleshooting:');
        console.error('  1. Check your .env file exists in backend/');
        console.error('  2. Verify HANA_HOST, HANA_USER, HANA_PASSWORD are correct');
        console.error('  3. Ensure HANA Cloud instance is running');
        console.error('  4. Check IP allowlist in SAP BTP');
        process.exit(1);
    }
    
    console.log('✅ Connected to HANA Cloud!\n');
    
    // Test query
    const testQuery = 'SELECT CURRENT_USER, CURRENT_SCHEMA, CURRENT_TIMESTAMP FROM DUMMY';
    console.log(`Running test query: ${testQuery}\n`);
    
    connection.exec(testQuery, (err, rows) => {
        connection.disconnect();
        
        if (err) {
            console.error('❌ Query FAILED\n');
            console.error('Error:', err.message);
            process.exit(1);
        }
        
        console.log('✅ Query executed successfully!\n');
        console.log('Results:');
        console.log(JSON.stringify(rows[0], null, 2));
        console.log('\n🎉 Connection test PASSED!\n');
        console.log('Next steps:');
        console.log('  1. Start the backend: npm start');
        console.log('  2. Test endpoint: http://localhost:3000/api/health');
        console.log('  3. Update frontend to call backend\n');
        process.exit(0);
    });
});
