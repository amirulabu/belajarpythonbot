# AGENTS.md

This file contains guidelines and commands for agentic coding assistants working on this codebase.

## Project Overview

This is a serverless Telegram bot built with Python using AWS SAM. The project consists of:
- **src/**: Main source code (Lambda functions, quiz logic, utilities)
- **tests/**: Unit and integration tests using pytest
- **template.yaml**: AWS SAM template defining serverless resources
- **Makefile**: Build, test, and deployment automation
- **pyproject.toml**: Poetry configuration for dependency management

## Development Commands

### Testing
```bash
# Run all unit tests (via Poetry)
make test

# Run tests with coverage report
make test-coverage

# Run a specific test file
poetry run pytest tests/unit/test_helper.py -sv

# Run a specific test function
poetry run pytest tests/unit/test_helper.py::test_fix_reply_markup -sv

# Run tests matching a keyword pattern
poetry run pytest tests/unit -k "fix_reply"
```

### Build & Deployment
```bash
# Build the SAM application
make build

# Deploy to AWS
make deploy

# Run locally for development
make run-local

# Setup environments
make setup         # Install production dependencies via Poetry
make setup-dev     # Install production + dev dependencies via Poetry

# Clean up
make clean         # Remove .venv and .pyc files
make cleanup       # Delete AWS CloudFormation stack
```

## Code Style Guidelines

### Import Order
1. Standard library imports (`os`, `json`, `traceback`, etc.)
2. Third-party imports (`boto3`, `requests`, etc.)
3. Local imports (`from errors import ...`, `from quiz import ...`)

Example:
```python
import os
import json
import traceback

import boto3
import requests

from errors import UnauthorizedException, EnvironmentException
from quiz import Quiz
from helper import send_message
```

### Formatting & Naming
- **Indentation**: 4 spaces
- **Classes**: PascalCase (`Quiz`, `UserDDB`, `UnauthorizedException`)
- **Functions/Variables**: snake_case (`send_message`, `fix_reply_markup_readable`)
- **Constants**: UPPER_SNAKE_CASE (`CONFIG`, `QUIZ_QUEUE_URL`)
- **Line length**: Follow standard Python conventions (~88-100 chars)

### Type Hints
- Type hints are minimal in this codebase
- Add type hints when creating new functions or modifying existing ones
- Use standard Python typing (`str`, `int`, `Dict`, `List`, `Optional`)

### Error Handling
- Use custom exceptions from `errors.py` (`UnauthorizedException`, `EnvironmentException`)
- Implement try-catch blocks with appropriate error responses
- Use the custom `logging()` function for debug output
- Always validate environment variables and raise `EnvironmentException` if missing

### File Structure
- **app.py**: Main API Gateway Lambda handler
- **quiz_worker.py**: SQS worker Lambda function
- **quiz.py**: Core quiz logic and Quiz class
- **helper.py**: Utility functions for Telegram API interaction
- **db_operation.py**: DynamoDB operations and UserDDB class
- **errors.py**: Custom exception classes
- **quiz_dict.py**: Quiz data and constants

## Testing Guidelines

### Test Structure
- Unit tests in `tests/unit/test_*.py`
- Integration tests in `tests/integration/`
- Test fixtures in `tests/unit/fixtures/`
- Python path automatically configured via pyproject.toml

### Testing Patterns
- Use pytest fixtures extensively
- Mock external dependencies with `pytest-mock`
- Use `monkeypatch` for environment variable testing
- Run tests via Poetry to ensure correct Python path

### Example Test Structure
```python
import pytest
from unittest.mock import Mock, patch

from helper import send_message

def test_send_message():
    mock_response = {"ok": True}
    with patch('requests.post', return_value=Mock(json=lambda: mock_response)):
        result = send_message("chat_id", "message")
        assert result["ok"] is True
```

## Dependencies

### Production (pyproject.toml [tool.poetry.dependencies])
- boto3==1.26.153
- requests==2.31.0
- Python ^3.9

### Development (pyproject.toml [tool.poetry.group.dev.dependencies])
- pytest==7.3.2
- pytest-cov==4.1.0
- pytest-mock==3.11.1

Note: Use Poetry for all dependency management. The project includes src/requirements.txt for AWS Lambda deployment but Poetry is the source of truth.

## Environment Setup
- Python 3.9+ (specified in pyproject.toml)
- Uses AWS SAM for local development and deployment
- DynamoDB for persistence, SQS for queuing, API Gateway for HTTP endpoints
- Poetry for dependency management

## Important Notes
- No linting tools configured - consider adding flake8/black for consistency
- Basic type checking only - add mypy for stronger type validation
- No pre-commit hooks - can be added for better code quality
- Always use `make` commands rather than direct sam/poetry commands when possible
- Poetry automatically sets PYTHONPATH to include src/ via pyproject.toml
