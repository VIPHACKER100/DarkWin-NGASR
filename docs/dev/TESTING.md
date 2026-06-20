# DARKWIN Testing Guide

## Test Suite Structure

```
tests/
+-- __init__.py
+-- test_robustness.py          # System-level robustness tests
+-- unit/
|   +-- test_core.py            # Core engine unit tests
+-- integration/
|   +-- test_db.py              # Database integration tests
+-- vuln_suite/
    +-- test_scanners.py        # Scanner module structure tests
```

## Running Tests

### CLI
```bash
# Run all tests
darkwin test

# Or directly via pytest
pytest tests/ -v

# With coverage
pytest tests/ --cov=core --cov=modules --cov-report=term-missing
```

### Specific Test Suites
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests (requires live PostgreSQL)
pytest tests/integration/ -v

# Vulnerability scanner tests
pytest tests/vuln_suite/ -v

# Robustness / edge-case tests
pytest tests/test_robustness.py -v
```

## Writing Tests

### Unit Test Pattern
```python
# tests/unit/test_core.py
import pytest
from core.cache_manager import CacheManager

class TestCacheManager:
    def test_load_default_config(self) -> None:
        pass
```

### Fixtures
Shared fixtures are in `conftest.py` at the project root:

```python
# conftest.py
import pytest

@pytest.fixture
def sample_config() -> dict:
    return {"timeout": 30, "max_threads": 5}

@pytest.fixture
def mock_scan_id() -> str:
    return "test-scan-001"
```

### Async Tests
Scanner modules use `asyncio`. Test with `pytest-asyncio`:

```python
@pytest.mark.asyncio
async def test_scanner_execution() -> None:
    result = await my_async_module.run("example.com", "scan-1", {})
    assert len(result) >= 0
```

## Exception Testing

Test that modules raise specific exceptions (not generic `Exception`):

```python
import httpx
import pytest

def test_api_failure() -> None:
    with pytest.raises(httpx.RequestError):
        make_bad_request()
```

## Mocking External Services

Use `unittest.mock` for API-dependent tests:

```python
from unittest.mock import patch

@patch("integrations.shodan_api.ShodanAPI.search")
def test_shodan_integration(mock_search) -> None:
    mock_search.return_value = {"matches": []}
```

## CI Pipeline

Tests run automatically via GitHub Actions on every push. The CI workflow:
1. Installs Python 3.11 + dependencies
2. Runs `pytest tests/ -v`
3. Verifies compilation with `python -m py_compile` on all files
4. Builds Docker images

## Compilation Verification

Before committing, verify all modified files compile:

```bash
python -m py_compile path/to/file.py
```

This is required because the project uses strict exception types — a bare `except:` or `except Exception:` will fail review.

## Test Coverage Goals

| Area | Target |
|------|--------|
| Core engine (config, logging, DB) | >80% |
| Vulnerability verifier | >90% |
| Stealth engine | >75% |
| Scanner modules | >60% |
| Integration paths | >50% |
