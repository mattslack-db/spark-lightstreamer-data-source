# AGENTS.md

This file provides guidance to LLMs when working with code in this repository.

You're an experienced Spark developer. You're developing a custom Python streaming data source to
read Lightstreamer real-time data using the PySpark DataSource API (Spark 4.0+).
You follow the architecture and development guidelines outlined below.

## Project Overview

This repository contains a Python data source (part of Apache Spark API) for
reading Lightstreamer streaming data (e.g. stock quotes, chat messages) in a streaming manner.

**Architecture**: Simple, flat structure with one data source per file. Each data source implements:
- `DataSource` base class with `name()`, `schema()`, and `streamReader()` methods
- `DataSourceStreamReader` for streaming reads with persistent connection
- Lightstreamer client wrapper for managing connections and subscriptions

### Documentation and examples of custom data sources using the same API

- https://github.com/alexott/cyber-spark-data-connectors
- https://github.com/databricks/tmm/tree/main/Lakeflow-OpenSkyNetwork
- https://spark.apache.org/docs/latest/api/python/tutorial/sql/python_data_source.html
- https://docs.databricks.com/aws/en/pyspark/datasources

## Architecture Patterns

### Data Source Implementation Pattern

1. **DataSource class** (`data_source.py`): Entry point
   - Implements `name()` class method (returns `"lightstreamer"`)
   - Implements `schema()` returning StructType from configured fields
   - Implements `streamReader()` for streaming read operations

2. **Stream Reader class** (`data_source.py`): Core streaming logic
   - Maintains persistent Lightstreamer connection across microbatches
   - Accumulates messages in a thread-safe queue between batches
   - `initialOffset()` returns starting offset
   - `latestOffset()` returns offset reflecting buffered messages
   - `partitions()` returns single partition with connection config
   - `read(partition)` drains buffered messages as rows
   - `commit()` and `stop()` for lifecycle management

3. **Client wrapper** (`lightstreamer_client.py`): Connection management
   - `LightstreamerClientManager` wraps the Lightstreamer SDK
   - Thread-safe message queue for subscription callbacks
   - Context manager support for clean connection lifecycle

### Key Design Principles

1. **SIMPLE over CLEVER**: No abstract base classes, factory patterns, or complex inheritance
2. **EXPLICIT over IMPLICIT**: Direct implementations, no hidden abstractions
3. **FLAT over NESTED**: Minimal class hierarchy
4. **Persistent connections**: Stream reader maintains connection across microbatches
5. **Lazy imports**: Import Lightstreamer SDK inside methods for partition-level execution

### Data Source Registration

```python
from lightstreamer_pyspark import LightstreamerDataSource
spark.dataSource.register(LightstreamerDataSource)

df = spark.readStream.format("lightstreamer") \
    .option("server_url", "http://localhost:8080") \
    .option("adapter_set", "DEMO") \
    .option("items", "item1,item2,item3") \
    .option("fields", "stock_name,last_price,time") \
    .option("mode", "MERGE") \
    .load()
```

## Development Commands

### Python Execution Rules

**CRITICAL: Always use `poetry run` instead of direct `python`:**
```bash
poetry run python script.py
```

### Setup
```bash
poetry install
```

### Testing
```bash
# Run unit tests only (default, skips integration)
poetry run pytest

# Run all tests including integration
poetry run pytest -m ""

# Run specific test file
poetry run pytest tests/test_lightstreamer_client.py
```

### Code Quality
```bash
poetry run ruff check src/
poetry run ruff format src/
poetry run mypy src/
```

## Testing Guidelines

- Tests use `pytest` with `pytest-spark` for Spark session fixtures
- Mock Lightstreamer client calls using `unittest.mock.patch`
- Integration tests require a running Lightstreamer server
- Use `@pytest.mark.integration` for tests needing a live server
