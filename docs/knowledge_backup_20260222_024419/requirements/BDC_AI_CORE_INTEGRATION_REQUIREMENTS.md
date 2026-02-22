# BDC-AI Core Integration for Batch Inference - Customer Requirements Summary

**Document Analysis Date**: 2026-01-28  
**Source**: BDC-FOS & AICore Integration.docx (v0.1, Sept 16, 2025)  
**Status**: Requirements extracted from PoC extended version document

---

## 1. OBJECTIVE

### Primary Goal
Enable native integration between **SAP Business Data Cloud (BDC) Feature Orchestration Service (FOS)** and **SAP AI Core** to support batch inference in AI workflows.

### Timeline
- **Short-term solution**: Q1 2026 (Custom transformer approach)
- **Long-term solution**: Q2 2026 (Plugin framework)

---

## 2. CORE CUSTOMER REQUIREMENTS

### 2.1 Functional Requirements

#### AI Core Use Case Support
Customer needs to support **3 types of AI Core use cases**:
1. **Training** (ArgoCD Workflow)
2. **Batch Inferencing**
   - API supports batch (Q1 '26)
   - Model applied on DataFrame (ArgoCD workflow)
3. **Real-time Inferencing/LLM**

**Primary Focus**: Batch inferencing integration

#### End-to-End Integration
- Seamless data flow from BDC-FOS to AI Core for batch processing
- Support for both initial data load and incremental data load
- Automated credential management (HDLFS certificates, AI Core tokens)

### 2.2 Technical Requirements

#### Architecture Requirements
1. **Multi-tenant support**
   - One AI Core resource group per FOS tenant
   - Cross-region support (AI Core creates one subaccount per region)
   
2. **Security & Authentication**
   - Use **BTP Credential Store** for secure credential management
   - HDLFS certificate rotation (< 3-day lifetime)
   - AI Core token management
   - No sensitive data in logs

3. **Data Access**
   - Support for HDLFS (Hadoop Distributed Lake File System) access
   - Use **delta-rs library** with Datafusion (not Delta Share)
   - Certificate-based authentication

4. **Resource Management**
   - AI Core resource group creation during data product provisioning
   - Mapping FOS tenants to AI Core resource groups
   - Support for 50+ resource groups (extendable)

### 2.3 Performance Requirements

1. **Data Volume Limits**
   - Support up to **1TB** (Datafusion single-node limitation)
   - Future exploration: Datafusion on Spark (Comet)

2. **Execution Time**
   - AI Core workflow startup: ~8 minutes
   - Prefer **fire-and-forget** approach for long-running jobs

3. **Cost Optimization**
   - Minimize read/write operations to reduce operational costs
   - Resource group-based pricing model

### 2.4 Operational Requirements

#### Observability
- Utilize existing BDC and AI Core monitoring tools
- Support for OpenTelemetry (OTEL) Collector integration
- Cloud Logging Systems (CLS) integration
- Argo workflow state monitoring

#### Quality Assurance
- Confirm end-to-end functionality with known datasets
- Support for multiple LoB (Line of Business) use cases:
  - Working Capital Insights (time series)
  - Predictive Cash Collection (classification)
  - Spend Control Tower

---

## 3. KEY TECHNICAL DECISIONS REQUIRED

### Decision Points from Document

1. **✅ RESOLVED**: Use custom transformer (not Delta Share)
2. **✅ RESOLVED**: Use delta-rs library (not HDLFS API)
3. **✅ RESOLVED**: BDC-FOS PySpark + AI Core combination (not full BDC-FOS control)
4. **⚠️ PENDING**: Configuration object creation timing
   - DPP (Data Product Provisioning) time vs. Transformation time
5. **⚠️ PENDING**: Tenancy mapping
   - One AI Core tenant per FOS region vs. per FOS tenant
6. **⚠️ PENDING**: Transformer design
   - One generic transformer vs. LoB-specific transformers

---

## 4. CONSTRAINTS & ASSUMPTIONS

### Technical Constraints
1. HDLFS certificates have **short lifetime** (< 3 days) → rotation required
2. **Single node** limitation for Datafusion (< 1TB data)
3. AI Core workflow startup time: **~8 minutes**
4. Resource group limit: **50 default** (can be extended)

### Assumptions
1. Docker registry secrets populated during tenant setup
2. Central git repository for all Argo Workflow Templates
3. BDC-FOS has access to AI Core API credentials
4. All AI Core credentials stored in BTP Credential Store
5. Security team validation for credential management approach

### Known Limitations
1. Only supporting batch inferencing where models are fetched from object store
2. Training pipeline must store model/metrics in HDLFS
3. Data volume < 1TB per job
4. PySpark vs. Datafusion performance benchmarking needed

---

## 5. PROPOSED IMPLEMENTATION APPROACH

### Short-term (Q1 2026): Custom Transformer
- **PySpark-based transformer** calling AI Core APIs
- Generic transformer for all LoB use cases
- Polling mechanism for job completion
- BTP Credential Store integration

### Long-term (Q2 2026): Plugin Framework
- **BDC FOS Plugin Extensibility Framework**
- Better separation of concerns
- OpenTelemetry integration
- Enhanced observability

### Alternative Approach (Under Evaluation)
**Kubernetes Job** instead of Spark Transformer:
- **Pros**: Optimal resource consumption, data volume agnostic, faster
- **Cons**: New approach, integration complexity, state management

---

## 6. STAKEHOLDER REQUIREMENTS

### Collaboration Needed
- **LoB Teams**: Validate practical use cases
- **Security Team**: Approve credential management approach
- **BDC Operations**: Certificate rotation ownership
- **AI Core Team**: Deployment support, resource group limits

### Deliverables Expected
1. End-to-end working solution in PoC/dev landscapes
2. Performance testing (boundary conditions)
3. Architecture Decision Records (ADRs)
4. Deployment guides
5. Pricing metrics documentation

---

## 7. SUCCESS CRITERIA

### Must Have
- ✅ Secure credential management (BTP Cred Store)
- ✅ Multi-tenant support (resource group per tenant)
- ✅ Automated certificate rotation
- ✅ End-to-end data flow (BDC-FOS → AI Core)
- ✅ Support for 1+ LoB use case

### Should Have
- ✅ Generic transformer (reusable across LoBs)
- ✅ Fire-and-forget execution pattern
- ✅ Observability via existing tools
- ✅ Performance within acceptable limits

### Nice to Have
- 🔄 Plugin framework (Q2 2026)
- 🔄 Support for > 1TB data volumes
- 🔄 Real-time inferencing support

---

## 8. OPEN QUESTIONS

1. **Tenancy Model**: One AI Core tenant per region or per FOS tenant?
2. **Configuration Timing**: Create AI Core configuration at provisioning or runtime?
3. **Certificate Management**: Who owns HDLFS cert rotation?
4. **Resource Limits**: How many resource groups can be supported per AI Core instance?
5. **Pricing**: How are tenants mapped to AI Core resource groups for billing?

---

## 9. NEXT STEPS (From Document)

1. **Immediate** (2 weeks, end of October):
   - Extend PoC to include end-to-end flows
   - Deploy to PoC/dev landscapes
   - Collaborate with LoB team for validation

2. **Short-term** (Q1 2026):
   - Implement custom transformer solution
   - Performance testing
   - Security validation

3. **Long-term** (Q2 2026):
   - Plugin framework implementation
   - OpenTelemetry integration
   - Enhanced observability

---

## 10. RELATED DOCUMENTATION

### References in Document
- ADR - BDC-BAI Integration for Batch Inference
- BDC-BAI Tenancy Mapping ADR
- WG_AI_ADR (Training and Grounding Workflows)
- BTP Cred Store Architecture
- AI Core SDK documentation
- Delta-rs code repository

### GitHub Repositories Mentioned
- `bdc-fos/dp-metadata` (Data product definitions)
- `bdc-fos/fos-workflows` (Transformer code)
- `delta-rs` (SAP fork for HDLFS support)
- `hanalytics-techoffice/aicore_cash_forecast` (Reference implementation)

---

## WHY THIS MATTERS

**User Constraint**: Customer needs batch AI inference at scale without managing infrastructure complexity.

**Problem Solved**: Current gap between BDC data products and AI Core batch processing.

**Business Value**: 
- Enables AI-powered insights on enterprise data
- Reduces operational overhead for AI workflows
- Supports multiple LoB use cases (Working Capital, Cash Collection, Spend Control)

**Technical Philosophy**: 
- Security-first approach (BTP Cred Store)
- Multi-tenant by design
- Practical over theoretical (fire-and-forget, existing tools)
- Iterative delivery (PoC → short-term → long-term)