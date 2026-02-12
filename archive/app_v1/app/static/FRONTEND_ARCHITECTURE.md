# Frontend Architecture - Dual UX Implementation

## Overview

This project supports TWO frontend implementations for A/B comparison:
1. **SAP UI5 / Fiori** - Enterprise SAP framework
2. **Alpine.js + Tailwind CSS** - Modern lightweight framework

## Directory Structure

```
app/static/
├── index.html              # Entry point with UX selector
├── ui5-app.html           # SAP UI5 application
├── alpine-app.html        # Alpine.js application
│
├── ui5/                   # SAP UI5 Implementation
│   ├── app.js            # Main UI5 app
│   ├── pages/            # UI5 page modules
│   │   ├── dataProductsPage.js
│   │   ├── apiPlaygroundPage.js
│   │   ├── loggingPage.js
│   │   ├── settingsPage.js
│   │   └── connectionsPage.js
│   └── components/       # Reusable UI5 components
│
├── alpine/               # Alpine.js Implementation
│   ├── app.js           # Main Alpine app
│   ├── components/      # Alpine components
│   │   ├── dataProducts.js
│   │   ├── apiPlayground.js
│   │   ├── logging.js
│   │   ├── settings.js
│   │   └── connections.js
│   └── styles/          # Tailwind config
│
├── shared/              # Shared between both UX
│   ├── api/            # API client libraries
│   │   ├── dataProductsAPI.js
│   │   ├── playgroundAPI.js
│   │   ├── loggingAPI.js
│   │   └── settingsAPI.js
│   └── utils/          # Common utilities
│
└── tests/
    ├── ui5/            # UI5-specific tests (OPA5)
    ├── alpine/         # Alpine-specific tests (Playwright)
    └── shared/         # API tests (work with both)
```

## Switching Between UX Implementations

### Method 1: URL Parameter
```
http://localhost:5000?ux=ui5      # SAP UI5 version
http://localhost:5000?ux=alpine   # Alpine.js version
http://localhost:5000             # Default (preference saved)
```

### Method 2: Feature Flag
```json
{
  "features": {
    "alpine_ux": {
      "enabled": true,
      "description": "Use Alpine.js UX instead of UI5"
    }
  }
}
```

### Method 3: Settings Page Toggle
- User selects UX preference
- Saved to localStorage
- Persists across sessions

## Backend API Compatibility

**Both UX implementations use the SAME backend APIs:**
- `/api/data-products/*` - Data Products operations
- `/api/playground/*` - API Playground
- `/api/logs/*` - Logging
- `/api/features/*` - Feature flags

This ensures:
- ✅ No backend changes needed
- ✅ True apples-to-apples comparison
- ✅ Can switch instantly
- ✅ Gradual migration possible (page by page)

## Testing Strategy

### UI5 Tests
- **OPA5** for UI5-specific component tests
- **Playwright** for E2E tests

### Alpine.js Tests
- **Playwright** for E2E tests (same tool!)
- **Vitest** for component unit tests
- **Testing Library** for DOM testing

### Shared Tests
- API integration tests (work with both UX)
- Backend tests (framework-agnostic)

## Migration Path

**Phase 1** (Current): Dual implementation
- ✅ Both UX complete and working
- ✅ User can compare side-by-side
- ✅ Make informed decision

**Phase 2**: Choose winner
- User decides which UX to keep
- Deprecate the other
- Clean up unused code

**Phase 3**: Gradual migration (if needed)
- Keep one page in old UX
- Migrate others to new UX
- Zero downtime

## Benefits of This Architecture

1. **Risk-Free Experimentation** - Can revert anytime
2. **Informed Decision** - Compare real implementations
3. **No Technical Debt** - Clean separation
4. **Team Onboarding** - New devs see both approaches
5. **Future-Proof** - Easy to add 3rd UX if needed

---

**Next**: Implementing Alpine.js version with full features + tests