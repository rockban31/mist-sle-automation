# Tests README

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install pytest pytest-cov responses
```

### Run All Tests

```bash
# Using pytest
pytest tests/

# Using unittest
python -m unittest discover tests/
```

### Run Specific Test

```bash
pytest tests/test_mist.py
pytest tests/test_logic.py
```

### With Coverage

```bash
pytest --cov=src tests/
```

---

## Test Structure

- `test_mist.py` - Tests for Mist API client
- `test_logic.py` - Tests for decision logic
- (To be added):
  - `test_diagnostics.py`
  - `test_remediation.py`
  - `test_validation.py`
  - `test_zendesk.py`
  - `test_splunk.py`

---

## Mocking

Tests use `unittest.mock` to mock external API calls:

```python
@patch('mist.requests.get')
def test_get_ap_stats(self, mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {...}
    mock_get.return_value = mock_response
    
    # Test code
```

---

## Future Enhancements

- [ ] Integration tests with Mist sandbox
- [ ] End-to-end workflow tests
- [ ] Performance tests
- [ ] Load tests for concurrent workflows

---

## Continuous Integration

Tests will run automatically on:
- Pull requests
- Merges to main branch
- Scheduled daily runs

Configure in `.github/workflows/test.yml` (to be created).
