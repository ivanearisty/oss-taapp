# HW2 Implementation Plan

## Service Selection
**Selected Service:** Issue Tracker (Trello API)
**Rationale:** 
- Well-documented REST API
- Clear OAuth 2.0 implementation
- Familiar CRUD operations (boards, lists, cards)
- Good testing opportunities

## Required Components (following HW1 pattern)

### A. Abstract API (`[service]_api`)
- Define the abstract contract (ABC) 
- Minimal interface defining service capabilities
- No external dependencies

### B. Concrete Implementation (`[service]_impl`) 
- Implements the abstract API
- **NEW: OAuth 2.0 flow implementation**
- Wraps external service API
- Secure credential storage

### C. FastAPI Service (`[service]_service`)
- Exposes implementation over HTTP
- OAuth endpoints
- Core functionality endpoints  
- Deployment-ready

### D. Auto-Generated Client (`[service]_service_api_client`)
- Generated from OpenAPI spec
- Type-safe network client

### E. Service Client Adapter (`[service]_adapter`)
- Implements abstract API
- Uses auto-generated client
- Location transparency

## Key Requirements for HW2

### Git Workflow
- [x] Create `hw2` main branch
- [ ] Feature branches for each component (`hw2-api-design`, `hw2-oauth-impl`, etc.)
- [ ] Squash and merge workflow
- [ ] Clean commit history

### Authentication 
- [ ] Proper OAuth 2.0 flow
- [ ] Secure credential storage in database
- [ ] Redirect URI handling (dev + prod)

### Code Quality
- [ ] MyPy passing (no type: ignore without reason)
- [ ] Ruff passing (minimal noqa comments)
- [ ] Comprehensive testing (unit, integration, e2e)
- [ ] Coverage requirements met

### Deployment
- [ ] Public cloud deployment (Render/Vercel/Fly.io/AWS/GCP)
- [ ] Environment variables secured
- [ ] CircleCI auto-deployment
- [ ] /health endpoint
- [ ] Document deployment process

### Timeline
- **First Run Submission:** Thursday (10/30) @ Midnight
- **Peer Review:** Sunday (11/2) @ Midnight  
- **Final Submission:** Friday (11/7) @ Midnight

## Next Steps
1. Choose service category
2. Create feature branch for API design
3. Implement OAuth 2.0 flow
4. Build core components
5. Deploy and test
