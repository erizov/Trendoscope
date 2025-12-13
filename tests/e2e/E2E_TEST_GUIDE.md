# E2E Test Suite Guide

## Overview

Comprehensive end-to-end test suite that validates all major Trendoscope features with detailed logging and statistics.

## Test Coverage

### ✅ News Fetching by Category
- Tests all 9 categories: `all`, `tech`, `politics`, `business`, `conflict`, `legal`, `society`, `science`, `general`
- Validates article structure (title, summary, link)
- Tracks articles fetched per category

### ✅ Translation Tests
- Tests translation to **English** (`en`)
- Tests translation to **Russian** (`ru`)
- Validates translation response format
- Checks translation quality

### ✅ Author Style Generation
Tests post generation in style of all 8 pretrained authors:
- **Russian Authors**: Tolstoy, Dostoevsky, Pushkin, Lermontov, Turgenev, Leskov
- **English Authors**: Mark Twain, William Faulkner
- Validates post structure and author style metadata

### ✅ API Endpoint Health Checks
- `/api/health` - Health check
- `/metrics` - Prometheus metrics
- `/api/balance/check` - Balance checking
- `/api/analytics/costs` - Cost analytics
- `/api/analytics/usage` - Usage statistics
- `/api/analytics/trends` - Trend analysis

### ✅ Error Handling
- Invalid category handling
- Invalid author style handling
- Missing translation parameters
- Error counting and reporting

## Running Tests

### Quick Start

1. **Start the server:**
   ```bash
   python run.py
   ```

2. **Run all E2E tests:**
   ```bash
   pytest tests/e2e/test_full_system.py -v
   ```

3. **Or use the standalone runner:**
   ```bash
   python tests/e2e/run_e2e_tests.py
   ```

### Advanced Usage

**Run specific test class:**
```bash
pytest tests/e2e/test_full_system.py::TestNewsFetching -v
pytest tests/e2e/test_full_system.py::TestAuthorStyles -v
```

**Run with detailed output:**
```bash
pytest tests/e2e/test_full_system.py -v -s
```

**Generate HTML report:**
```bash
pytest tests/e2e/test_full_system.py --html=test_results/report.html --self-contained-html
```

**Run only failed tests:**
```bash
pytest tests/e2e/test_full_system.py --lf
```

## Test Statistics

The test suite automatically tracks:

- **Total Tests**: All tests executed
- **Passed/Failed**: Success/failure counts
- **Categories Tested**: Which news categories were tested
- **Authors Tested**: Which author styles were tested
- **Translations Tested**: Number of translation tests
- **API Endpoints Tested**: Which endpoints were checked
- **Articles Fetched**: Total articles retrieved
- **Posts Generated**: Total posts generated
- **Test Duration**: Total execution time
- **Errors**: Detailed error list with timestamps

## Test Reports

### JSON Report
After running tests, a detailed JSON report is saved to:
```
test_results/e2e_report.json
```

**Report Structure:**
```json
{
  "statistics": {
    "total_tests": 50,
    "passed_tests": 48,
    "failed_tests": 2,
    "categories_tested": ["all", "tech", "politics", ...],
    "authors_tested": ["tolstoy", "dostoevsky", ...],
    "translations_tested": 2,
    "api_endpoints_tested": ["/api/health", "/metrics", ...],
    "articles_fetched": 45,
    "posts_generated": 8,
    "test_duration": 120.5,
    "errors": [...]
  },
  "logs": [...],
  "summary": {
    "total": 50,
    "passed": 48,
    "failed": 2,
    "success_rate": 96.0,
    "duration_seconds": 120.5
  }
}
```

### HTML Report
Visual HTML report with:
- Test results overview
- Pass/fail status
- Execution times
- Error details
- Screenshots (if configured)

## Logging

All test events are logged with:
- **Timestamp**: When the event occurred
- **Level**: INFO, ERROR, WARNING
- **Message**: Human-readable description
- **Data**: Additional context

**Log Levels:**
- `INFO`: Test passed, operation successful
- `ERROR`: Test failed, error occurred
- `WARNING`: Non-critical issue

## Error Handling

The test suite includes comprehensive error handling:

1. **Connection Errors**: Handles server not running
2. **Timeout Errors**: Handles slow responses
3. **Invalid Responses**: Validates response format
4. **Missing Data**: Handles empty responses gracefully

All errors are:
- Logged with full context
- Counted in statistics
- Included in final report
- Timestamped for debugging

## Continuous Integration

### GitHub Actions Example
```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python run.py &
      - run: sleep 10
      - run: pytest tests/e2e/test_full_system.py -v
      - uses: actions/upload-artifact@v2
        if: always()
        with:
          name: test-results
          path: test_results/
```

## Troubleshooting

### Server Not Running
```
❌ Server is not running: Connection refused
```
**Solution**: Start the server with `python run.py`

### Timeout Errors
```
❌ Test failed: Request timeout
```
**Solution**: Increase timeout in test configuration or check server performance

### Invalid Response Format
```
❌ Test failed: Invalid response format
```
**Solution**: Check API endpoint implementation matches expected format

## Best Practices

1. **Run tests before deployment**: Ensure all features work
2. **Check reports regularly**: Monitor success rates
3. **Fix errors promptly**: Address failing tests immediately
4. **Update tests with features**: Add tests for new functionality
5. **Review statistics**: Track trends in test results

## Test Maintenance

### Adding New Tests

1. Add test method to appropriate test class
2. Use `test_stats.record_test()` to track results
3. Update category/author lists if needed
4. Run tests to verify

### Updating Test Configuration

Edit constants in `test_full_system.py`:
```python
API_URL = "http://localhost:8003"
TEST_CATEGORIES = [...]
AUTHORS = [...]
```

## Performance

Typical test execution time: **2-5 minutes**

Factors affecting duration:
- Number of categories tested
- Number of authors tested
- Server response time
- Network latency

## Next Steps

- [ ] Add performance benchmarks
- [ ] Add load testing
- [ ] Add visual regression tests
- [ ] Add API contract tests
- [ ] Integrate with monitoring

