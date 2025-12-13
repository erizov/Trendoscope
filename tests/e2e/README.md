# E2E Test Suite

Comprehensive end-to-end tests for Trendoscope system.

## Features Tested

1. **News Fetching by Category**
   - Tests all categories: all, tech, politics, business, conflict, legal, society, science, general
   - Validates article structure and content

2. **Translation**
   - Tests translation to English and Russian
   - Validates translation quality and response format

3. **Author Style Generation**
   - Tests all 8 pretrained authors:
     - Tolstoy, Dostoevsky, Pushkin, Lermontov
     - Turgenev, Leskov, Mark Twain, Faulkner
   - Validates post generation in each author's style

4. **API Endpoint Health**
   - Health check endpoint
   - Metrics endpoint
   - Balance check endpoint
   - Analytics endpoints

5. **Error Handling**
   - Invalid category handling
   - Invalid author style handling
   - Missing translation parameters

## Running Tests

### Run all E2E tests:
```bash
pytest tests/e2e/test_full_system.py -v
```

### Run specific test class:
```bash
pytest tests/e2e/test_full_system.py::TestNewsFetching -v
```

### Run with detailed output:
```bash
pytest tests/e2e/test_full_system.py -v -s
```

### Run and save HTML report:
```bash
pytest tests/e2e/test_full_system.py --html=test_results/report.html --self-contained-html
```

## Test Statistics

The test suite automatically tracks:
- Total tests run
- Passed/failed counts
- Categories tested
- Authors tested
- Translations tested
- API endpoints tested
- Articles fetched
- Posts generated
- Error details

## Test Report

After running tests, a detailed JSON report is saved to:
- `test_results/e2e_report.json`

The report includes:
- Complete statistics
- All test logs
- Error details
- Summary with success rate

## Configuration

Set `API_URL` in `test_full_system.py` if your API runs on a different port:
```python
API_URL = "http://localhost:8003"
```

## Prerequisites

1. Start the Trendoscope server:
   ```bash
   python run.py
   ```

2. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-html httpx
   ```

## Test Structure

```
tests/e2e/
├── test_full_system.py    # Main test suite
├── conftest.py            # Pytest configuration
└── README.md             # This file
```

## Continuous Integration

These tests can be integrated into CI/CD pipelines:
```yaml
- name: Run E2E Tests
  run: |
    python run.py &
    sleep 5
    pytest tests/e2e/test_full_system.py -v
```

