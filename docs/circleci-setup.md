# CircleCI Setup Guide

This document explains how to set up and configure CircleCI for the Python Application Template project. The CI/CD pipeline is designed to ensure code quality, run comprehensive tests, and maintain high standards across all environments.

## Overview

The project uses CircleCI with a multi-job workflow that includes:

- **Build**: Environment setup and dependency installation using `uv`
- **Lint**: Code formatting and style checks with `ruff`
- **Unit Tests**: Fast, isolated tests with coverage reporting
- **CircleCI Tests**: Integration tests that work without local credentials
- **Integration Tests**: Full API tests with real Gmail credentials (protected branches only)
- **Report Summary**: Consolidated test results and coverage reporting

## Prerequisites

Before setting up CircleCI, ensure you have:

1. A GitHub repository with this codebase
2. A CircleCI account connected to your GitHub
3. Gmail API credentials (for integration tests)

## Initial Setup

### 1. Connect Repository to CircleCI

1. Log in to [CircleCI](https://circleci.com/)
2. Navigate to "Projects" in the left sidebar
3. Find your repository and click "Set Up Project"
4. CircleCI will automatically detect the `.circleci/config.yml` file

### 2. Configure Environment Variables

For integration tests to work properly, you need to set up environment variables in CircleCI:

#### Required Environment Variables

Create a **Context** named `gmail-client` with the following variables:

| Variable Name | Description | Example Value |
|---------------|-------------|---------------|
| `GMAIL_CLIENT_ID` | OAuth2 client ID from Google Cloud Console | `202143129121-...apps.googleusercontent.com` |
| `GMAIL_CLIENT_SECRET` | OAuth2 client secret | `GOCSPX-...` |
| `GMAIL_REFRESH_TOKEN` | OAuth2 refresh token | `1//05nE4gmCcmtjx...` |
| `GMAIL_TOKEN_URI` | OAuth2 token endpoint | `https://oauth2.googleapis.com/token` |
| `GMAIL_SCOPES` | Gmail API scopes | `https://www.googleapis.com/auth/gmail.modify` |
| `GMAIL_UNIVERSE_DOMAIN` | Google API universe domain | `googleapis.com` |

#### Setting Up the Context

1. In CircleCI, go to **Organization Settings** → **Contexts**
2. Click **Create Context**
3. Name it `gmail-client`
4. Add each environment variable listed above

## Workflow Structure

The project has two main workflows:

### 1. Build and Test (All Branches)

Runs on every push and pull request:

```yaml
build_and_test:
  jobs:
    - build
    - lint (requires: build)
    - unit_test (requires: build)
    - circleci_test (requires: unit_test)
    - report_summary (requires: unit_test, circleci_test)
```

### 2. Full Integration (Protected Branches)

Runs only on `main` and `develop` branches with real API credentials:

```yaml
full_integration:
  jobs:
    - build
    - lint (requires: build)
    - unit_test (requires: build)
    - circleci_test (requires: unit_test)
    - integration_test (requires: circleci_test, context: gmail-client)
    - report_summary (requires: all)
```

## Job Details

### Build Job

- **Purpose**: Sets up the environment and installs dependencies
- **Key Actions**:
  - Installs `uv` package manager
  - Creates Python 3.11 virtual environment
  - Runs `uv sync --all-packages` to install all workspace dependencies
  - Persists the entire workspace for subsequent jobs

### Lint Job

- **Purpose**: Ensures code quality and formatting standards
- **Tool**: `ruff` for linting and formatting
- **Command**: `ruff check .`

### Unit Test Job

- **Purpose**: Runs fast, isolated tests with coverage
- **Coverage**: Minimum 85% required
- **Outputs**: JUnit XML and coverage reports
- **Includes**: Static analysis with `mypy`

### CircleCI Test Job

- **Purpose**: Runs integration tests that don't require local credentials
- **Scope**: All tests marked with `not local_credentials`
- **Environment**: Uses CircleCI environment variables

### Integration Test Job

- **Purpose**: Full API testing with real Gmail credentials
- **Restrictions**: Only runs on protected branches (`main`, `develop`)
- **Context**: Uses `gmail-client` context for credentials
- **Scope**: Tests marked with `integration and not local_credentials`

### Report Summary Job

- **Purpose**: Consolidates test results and coverage information
- **Outputs**: Summary of all test runs and coverage metrics

## Local Development

To run the same checks locally that CircleCI runs:

```bash
# Install dependencies
uv sync --all-packages --extra dev

# Run linting
uv run ruff check .

# Run unit tests with coverage
uv run pytest src/ --cov=src --cov-fail-under=85

# Run all tests except those requiring local credentials
uv run pytest src/ tests/ -m "not local_credentials"

# Run static analysis
uv run mypy src/
```

## Troubleshooting

### Common Issues

#### 1. "Extra 'dev' is not defined" Error

This happens if the project uses legacy `[dependency-groups]` instead of `[project.optional-dependencies]`. Ensure your `pyproject.toml` uses the modern format:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.4.1",
    # ... other dev dependencies
]
```

#### 2. Environment Variables Not Available

- Verify the `gmail-client` context is created with all required variables
- Ensure the context is applied to the `integration_test` job
- Check that you're running on a protected branch (`main` or `develop`)

#### 3. Coverage Threshold Failures

- The project requires 85% code coverage
- Add tests for uncovered code or adjust the threshold in `pyproject.toml`
- Check the coverage report artifacts for detailed information

#### 4. uv Command Issues

- Ensure you're using pure `uv` commands, not `uv pip`
- Use `uv tree` instead of `uv pip list`
- Use `uv add` instead of `uv pip install`

### Debugging Steps

1. **Check Build Logs**: Look at the detailed output from each job
2. **Review Artifacts**: Download test results and coverage reports
3. **Test Locally**: Reproduce issues in your local environment
4. **Verify Configuration**: Ensure `.circleci/config.yml` matches this documentation

## Security Considerations

1. **Sensitive Data**: Never commit credentials to the repository
2. **Context Protection**: Restrict the `gmail-client` context to specific projects
3. **Branch Protection**: Integration tests only run on protected branches
4. **Environment Variables**: Use CircleCI contexts, not project-level environment variables

## Maintenance

### Updating Dependencies

When updating dependencies in `pyproject.toml`:

1. Update the lock file: `uv lock`
2. Test locally with the new dependencies
3. Commit both `pyproject.toml` and `uv.lock`
4. Monitor the CI pipeline for any issues

### Adding New Tests

When adding tests that require credentials:

- Mark them with `@pytest.mark.local_credentials` if they need local files
- Mark them with `@pytest.mark.integration` for API tests
- Ensure they work with environment variables for CI

### Modifying the Pipeline

When changing `.circleci/config.yml`:

1. Validate the YAML syntax
2. Test changes on a feature branch first
3. Consider the impact on build time and resource usage
4. Update this documentation if the workflow changes

## References

- [CircleCI Documentation](https://circleci.com/docs/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [pytest Documentation](https://docs.pytest.org/)
