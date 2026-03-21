# Test Suite Documentation

This directory contains the test suite for the Lightstreamer PySpark Source connector.

## Test Files

### `test_lightstreamer_client.py`
Unit tests for the Lightstreamer client wrapper components:
- Message queue functionality
- Subscription listener behavior
- Client manager operations
- Connection lifecycle

**Run with:**
```bash
pytest tests/test_lightstreamer_client.py -v
```

### `test_integration.py`
Integration tests that require a running Lightstreamer server:
- Full streaming pipeline tests
- Custom schema handling
- Docker-based server integration

**Requirements:**
- Docker installed and running
- Or a local Lightstreamer server at `http://localhost:8080`

**Run with:**
```bash
# With Docker (recommended)
cd docker && docker-compose up -d
pytest tests/test_integration.py -v

# Skip if Docker not available
SKIP_INTEGRATION=1 pytest tests/test_integration.py -v
```

### `test_public_demo.py`
Tests using Lightstreamer demo adapters (CHAT_ROOM and QUOTE_ADAPTER):
- CHAT_ROOM: Chat demo adapter with DISTINCT mode
- QUOTE_ADAPTER: Stock quotes with MERGE mode
- Connection lifecycle tests
- Performance tests

**Setup Options:**

#### Option 1: Local Server (Recommended)
```bash
# Use the Docker setup in this project
cd docker && docker-compose up -d

# Run tests against local server
pytest tests/test_public_demo.py -v
```

#### Option 2: Custom Server
```bash
# Set custom server URL
export LIGHTSTREAMER_SERVER=http://your-server:8080
pytest tests/test_public_demo.py -v
```

#### Option 3: Skip These Tests
```bash
SKIP_PUBLIC_DEMO=1 pytest tests/test_public_demo.py -v
```

**Adapter Requirements:**

The tests expect these adapters to be configured:

1. **DEMO Adapter Set** (includes QUOTE_ADAPTER)
   - Pre-installed with Lightstreamer Server
   - Items: `item1`, `item2`, ... `item30`
   - Fields: `stock_name`, `last_price`, `time`, `pct_change`, `bid`, `ask`, etc.
   - Mode: MERGE

2. **CHAT_ROOM Adapter**
   - Deploy from: https://github.com/Lightstreamer/Lightstreamer-example-Chat-adapter-java
   - Items: `chat_room`
   - Fields: `message`, `raw_timestamp`, `IP`
   - Mode: DISTINCT

## Running All Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=lightstreamer_pyspark --cov-report=html

# Run only fast tests (skip slow/integration)
pytest tests/ -v -m "not slow"

# Run with verbose output
pytest tests/ -v -s
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LIGHTSTREAMER_SERVER` | Server URL for demo adapter tests | `http://localhost:8080` |
| `SKIP_INTEGRATION` | Skip integration tests | `0` (run tests) |
| `SKIP_PUBLIC_DEMO` | Skip demo adapter tests | `0` (run tests) |

## Test Markers

- `@pytest.mark.integration`: Requires Docker/server
- `@pytest.mark.slow`: Long-running tests
- `@pytest.mark.skipif`: Conditional skip based on environment

## CI/CD Usage

```bash
# Quick CI run (unit tests only)
SKIP_INTEGRATION=1 SKIP_PUBLIC_DEMO=1 pytest tests/ -v

# Full CI run (with Docker)
docker-compose -f docker/docker-compose.yml up -d
pytest tests/ -v
docker-compose -f docker/docker-compose.yml down
```

## Troubleshooting

### No messages received in demo tests

The demo adapter tests are designed to handle cases where adapters might not be actively generating data:
- Tests will skip validation if no messages are received
- Check that Lightstreamer server is running: `curl http://localhost:8080`
- Verify adapters are deployed in `conf/adapters.xml`
- Check server logs for adapter errors

### Docker connection issues

```bash
# Check if container is running
docker ps | grep lightstreamer

# View logs
docker-compose -f docker/docker-compose.yml logs

# Restart
docker-compose -f docker/docker-compose.yml restart
```

### Import errors

```bash
# Ensure package is installed
pip install -e .

# Verify installation
python -c "import lightstreamer_pyspark; print('OK')"
```

## Test Development

When adding new tests:
1. Use appropriate fixtures from existing test files
2. Add docstrings explaining what's being tested
3. Use descriptive assertion messages
4. Clean up resources in `finally` blocks or use context managers
5. Mark slow tests with `@pytest.mark.slow`
6. Document any special setup requirements

## Example Test Session

```bash
# 1. Setup environment
cd /path/to/lightstreamer-pyspark-source
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[test]"

# 2. Start server
cd docker
docker-compose up -d
cd ..

# 3. Run tests
pytest tests/ -v -s

# 4. Cleanup
docker-compose -f docker/docker-compose.yml down
```

## Additional Resources

- [Lightstreamer Documentation](https://lightstreamer.com/docs/)
- [PySpark Testing Guide](https://spark.apache.org/docs/latest/api/python/getting_started/testing_pyspark.html)
- [pytest Documentation](https://docs.pytest.org/)

