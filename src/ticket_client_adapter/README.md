# Ticket Client Adapter

**Wraps the auto-generated client with the clean `TicketServiceAPI` interface.**

## Purpose

This adapter sits between your application code and the auto-generated HTTP client, providing:
- Clean domain interface (`TicketServiceAPI`)
- Location transparency (swap local/remote)
- Hides all HTTP/network details
- Leverages the type-safe generated client internally

## Architecture
```
Your Application Code
        ↓
  TicketServiceAPI (interface)
        ↓
  RemoteTicketService (adapter) ← YOU ARE HERE
        ↓
  Auto-Generated Client (HTTP details)
        ↓
  FastAPI Service
```

The adapter **wraps** the generated client, translating between:
- Domain models (`Ticket`, `Comment`) ↔ Generated models (`TicketResponse`, `CommentResponse`)
- Clean async methods ↔ HTTP-aware `asyncio_detailed()` calls
- Simple exceptions ↔ HTTP status codes

## Benefits

### 1. Best of Both Worlds
- Uses the **auto-generated client** internally (type-safe, auto-synced)
- Exposes the **domain interface** externally (clean, location-transparent)

### 2. Same Code, Different Implementation
```python
# config.py
def get_ticket_service() -> TicketServiceAPI:
    if os.getenv("USE_REMOTE"):
        # Remote via HTTP
        from ticket_client_adapter import RemoteTicketService
        return RemoteTicketService(...)
    else:
        # Local via direct Jira API
        from ticket_impl import TicketImpl
        return TicketImpl(...)

# app.py - IDENTICAL code for both!
service = get_ticket_service()
ticket = await service.create_ticket(...)
```

### 3. No HTTP in Your Business Logic
```python
# Clean domain code
async def create_bug_report(
    service: TicketServiceAPI,  # Interface, not implementation
    title: str,
    description: str
) -> Ticket:
    return await service.create_ticket(
        title=title,
        description=description,
        reporter="system",
        priority=TicketPriority.HIGH
    )

# Works with TicketImpl OR RemoteTicketService!
```

## Usage
```python
from ticket_client_adapter import RemoteTicketService
from ticket_api import TicketPriority, TicketStatus

async with RemoteTicketService(
    base_url="http://localhost:8000",
    user_id="user123",
    project_key="PROJ"
) as service:
    # Same interface as TicketImpl - no HTTP details!
    ticket = await service.create_ticket(
        title="Bug Report",
        description="Something broke",
        reporter="user@example.com",
        priority=TicketPriority.HIGH
    )
    
    # Clean, domain-focused API
    tickets = await service.list_tickets(status=TicketStatus.OPEN)
    comment = await service.add_comment(
        ticket.id,
        "dev@example.com",
        "Working on it"
    )
```

## Comparison

| Aspect | Direct Generated Client | Adapter (This) |
|--------|------------------------|----------------|
| **Interface** | HTTP-specific | `TicketServiceAPI` |
| **Usage** | `response = await create_ticket.asyncio_detailed(...)` | `ticket = await service.create_ticket(...)` |
| **Type checking** | `Client` specific | `TicketServiceAPI` polymorphic |
| **HTTP details** | Exposed (status codes, headers) | Hidden |
| **Location transparency** | Always remote | Swappable |
| **Mocking** | Mock HTTP calls | Mock interface |
| **Updates** | Auto-sync from OpenAPI | Manual wrapper update |

## When to Use What

**Use the Adapter (`RemoteTicketService`) when:**
- Building application features (business logic)
- Want location transparency (dev/prod different)
- Prefer clean, domain-focused code
- Need to mock at interface level

**Use the Generated Client directly when:**
- Need HTTP-level control (status codes, headers)
- Building monitoring/debugging tools
- Want automatic sync with API changes
- Don't need interface compatibility

## Testing

The adapter is fully tested with respx mocking:
```bash
uv run pytest src/ticket_client_adapter/tests/ -v
```

All 10 tests pass, covering:
- CRUD operations
- Comment management
- Error handling (404s)
- Context manager behavior

## Implementation Note

This adapter **wraps** the auto-generated client (`ticket_service_client`), not direct httpx calls. This means:
- Type safety from generated models
- Automatic updates when regenerating client
- Clean separation of concerns
- Best practices: composition over reimplementation

Example internal implementation:
```python
async def create_ticket(self, title, description, reporter, ...) -> Ticket:
    # 1. Convert to generated model
    request = TicketCreateRequest(title=title, ...)
    
    # 2. Call generated client
    response = await create_ticket_api_v1_tickets_post.asyncio_detailed(
        client=self._client, body=request, ...
    )
    
    # 3. Convert back to domain model
    return self._to_domain_ticket(response.parsed)
```
