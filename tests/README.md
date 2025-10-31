# Integration and End-to-End Tests

This directory contains comprehensive integration and end-to-end tests for the ticket management application.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                          # Shared fixtures
├── integration/                         # Integration tests
│   ├── test_service_adapter_integration.py  # Service + adapter layer tests
│   └── test_multi_component_workflow.py     # Multi-component workflows
└── e2e/                                 # End-to-end tests
    └── test_e2e_workflows.py            # Complete application workflows
```

## Test Categories

### Integration Tests (`tests/integration/`)

These tests verify that multiple components work together correctly:

#### `test_service_adapter_integration.py`
- **TestServiceEndpointsWithMockedBackend**: Tests FastAPI service endpoints with mocked backend
  - `test_create_ticket_through_service`: POST /api/v1/tickets
  - `test_get_ticket_through_service`: GET /api/v1/tickets/{id}
  - `test_update_ticket_through_service`: PATCH /api/v1/tickets/{id}
  - `test_delete_ticket_through_service`: DELETE /api/v1/tickets/{id}
  - `test_list_tickets_through_service`: GET /api/v1/tickets
  - `test_add_comment_through_service`: POST /api/v1/tickets/{id}/comments
  - `test_get_comments_through_service`: GET /api/v1/tickets/{id}/comments

- **TestServiceInputValidation**: Tests input validation and error handling
  - `test_missing_required_headers`: Validates header requirements
  - `test_invalid_priority_value`: Rejects invalid enum values
  - `test_empty_title_rejected`: Validates non-empty title

#### `test_multi_component_workflow.py`
- **TestTicketLifecycleWorkflow**: Complete lifecycle workflows
  - `test_complete_ticket_lifecycle`: Create → Update → Comment → Resolve workflow

- **TestBulkOperationWorkflow**: Multi-ticket operations
  - `test_filter_and_bulk_update`: Filter and bulk update tickets
  - `test_concurrent_ticket_updates`: Concurrent update handling

- **TestErrorRecoveryWorkflow**: Error handling and recovery
  - `test_recover_from_backend_failure`: Graceful failure handling
  - `test_invalid_ticket_id_handling`: Non-existent resource handling

### End-to-End Tests (`tests/e2e/`)

These tests verify complete application workflows from user perspective:

#### `test_e2e_workflows.py`
- **TestE2ETicketManagement**: Complete team collaboration scenarios
  - `test_e2e_team_collaboration_workflow`: Manager creates → Developer works → Manager reviews
  - `test_e2e_bug_tracking_workflow`: User reports → Triager assigns → Developer fixes

- **TestE2EDataConsistency**: Data consistency verification
  - `test_e2e_data_consistency_with_concurrent_operations`: Concurrent read consistency

- **TestE2EErrorScenarios**: Error handling in complete workflows
  - `test_e2e_graceful_degradation`: Partial failure handling

## Running Tests

### Run all tests
```bash
python -m pytest tests/ -v
```

### Run integration tests only
```bash
python -m pytest tests/integration/ -v
```

### Run e2e tests only
```bash
python -m pytest tests/e2e/ -v
```

### Run with coverage report
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Run specific test class
```bash
python -m pytest tests/integration/test_service_adapter_integration.py::TestServiceEndpointsWithMockedBackend -v
```

### Run specific test
```bash
python -m pytest tests/integration/test_service_adapter_integration.py::TestServiceEndpointsWithMockedBackend::test_create_ticket_through_service -v
```

## Test Fixtures

Shared fixtures are defined in `conftest.py`:

- **event_loop**: Event loop for async tests
- **http_client**: AsyncClient for testing the FastAPI app
- **mock_ticket_service**: Mock TicketServiceAPI implementation
- **sample_ticket**: Single sample ticket
- **sample_ticket_with_comments**: Ticket with comments
- **sample_tickets_list**: List of multiple tickets

## Key Testing Patterns

### 1. Mocking the Backend Service
```python
def test_create_ticket(self, sample_ticket):
    client = TestClient(app)
    with patch("ticket_service.main.get_ticket_service") as mock_get_service:
        mock_service = AsyncMock()
        mock_service.create_ticket.return_value = sample_ticket
        mock_get_service.return_value = mock_service

        response = client.post("/api/v1/tickets", json={...})
        assert response.status_code == 201
```

### 2. Testing Complete Workflows
The tests simulate real-world scenarios with multiple steps:
- Create resource
- Update resource
- Add comments
- Change status
- Verify final state

### 3. Error Handling
Tests verify graceful degradation:
- Missing required fields
- Invalid enum values
- Backend service failures
- Non-existent resources

## Authentication for Tests

The service uses OAuth token verification via the `get_user_tokens()` function. For testing:

1. **Test User IDs**: Use "test-" prefixed user IDs (e.g., "test-user-001")
   - These bypass OAuth token verification
   - Perfect for integration/unit tests

2. **Mock Token Storage**: Tests can mock `get_user_tokens()` to return tokens

3. **Headers Required**:
   - `X-User-ID`: User identifier (use "test-" prefix for tests)
   - `X-Project-Key`: Jira project key

## Coverage Requirements

The project requires **90% minimum test coverage**. Integration and e2e tests contribute to this goal.

Current coverage targets:
- Unit tests: Core functionality
- Integration tests: Component interactions
- E2E tests: Complete workflows

Run coverage report:
```bash
python -m pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

## Best Practices

1. **Use Fixtures**: Leverage pytest fixtures for common test data
2. **Test User IDs**: Always use "test-" prefix for test users
3. **Mock External Services**: Don't call real Jira in integration tests
4. **Clear Test Names**: Test names should describe the scenario
5. **Docstrings**: Include docstrings explaining what each test validates
6. **Assertions**: Use specific assertions (not just `assert response`)

## Adding New Tests

To add new integration tests:

1. Create test file in appropriate directory
2. Use `@pytest.mark.integration` or `@pytest.mark.e2e` decorator
3. Create test functions with clear names
4. Use fixtures from `conftest.py`
5. Mock external dependencies
6. Use "test-" prefixed user IDs
7. Add docstrings explaining the scenario

Example:
```python
@pytest.mark.integration
def test_new_feature(sample_ticket):
    """Test description of what this validates."""
    client = TestClient(app)
    with patch("ticket_service.main.get_ticket_service") as mock_get_service:
        mock_service = AsyncMock()
        # Set up mock...

        response = client.post(...)
        assert response.status_code == 201
```

## Continuous Integration

These tests are run on CircleCI for each commit. Tests must:
- Pass locally before pushing
- Have 90%+ coverage
- Use pytest markers correctly
- Not require local credentials (except marked tests)
