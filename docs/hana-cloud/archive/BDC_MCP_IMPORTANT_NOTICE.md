# ⚠️ IMPORTANT: BDC MCP Documentation Notice

**Date**: 2026-01-23  
**Status**: **DEVELOPMENT ONLY - NOT FOR PRODUCTION USE**

---

## Critical Information

### What is the "BDC MCP" in this documentation?

The BDC MCP references in this repository (`BDC_MCP_API_CATALOG.md`, `BDC_MCP_CSN_RETRIEVAL_GUIDE.md`) refer to:

**LOCAL PROTOTYPE MCP SERVER ONLY**
- ❌ **NOT a production SAP service**
- ❌ **NOT SAP's HANA Cloud BDC service**
- ❌ **NOT to be used in this project**
- ❌ **NOT deployable to BTP Cloud Foundry**

### What it actually is:

- A **local development tool** running in Cline IDE
- Connects to a **prototype sandbox environment**
- Used for **experimentation and testing only**
- **Cannot be used in production applications**

### Why this matters:

When building applications for **BTP Cloud Foundry deployment**, you **CANNOT**:
- ❌ Depend on local MCP servers
- ❌ Use sandbox/prototype services
- ❌ Expect these tools to be available in production

### For Production Applications:

Your BTP-deployed applications must use:
- ✅ Public SAP APIs with proper authentication
- ✅ SAP HANA Cloud native services
- ✅ BTP service bindings and destinations
- ✅ Self-contained, deployable solutions

---

## Documentation Status

The following documents are **DEVELOPMENT/REFERENCE ONLY**:

1. `BDC_MCP_API_CATALOG.md` - Local MCP tool reference
2. `BDC_MCP_CSN_RETRIEVAL_GUIDE.md` - Local MCP workflow guide

**These documents should be:**
- Treated as reference for understanding data structures
- NOT used as implementation guides for production features
- Considered part of research/exploration phase only

---

## Recommended Approach for Production

For accessing CSN schemas and data product information in production:

### Option 1: Check Your HANA Cloud Instance
- Verify if BDC (Business Data Cloud) service is enabled
- Use HANA SQL to query data product metadata
- Access CSN through HANA's native APIs

### Option 2: SAP API Business Hub
- Research official SAP APIs for data products
- Use proper OAuth/API key authentication
- Implement standard REST API calls

### Option 3: Static CSN Files (Last Resort)
- Pre-download CSN files during development
- Store in application repository
- Serve as static resources
- Note: Requires manual updates

---

## Action Items

If you need CSN/data product information for production:

1. ✅ **DO NOT use local BDC MCP**
2. ✅ Verify HANA Cloud capabilities
3. ✅ Research official SAP APIs
4. ✅ Use proper authentication mechanisms
5. ✅ Test in BTP environment early

---

## Summary

**The BDC MCP is a local development prototype tool that cannot be used in production applications. All production features must use official SAP services and APIs that are available in BTP Cloud Foundry.**

For questions about production-ready solutions, consult:
- SAP HANA Cloud documentation
- SAP BTP documentation  
- SAP API Business Hub
- Your SAP architect/consultant

---

**Last Updated**: 2026-01-23  
**Applies To**: All BDC_MCP_* documentation files