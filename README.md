# Lightstreamer PySpark Data Source

A custom PySpark streaming data source for consuming real-time data from [Lightstreamer](https://lightstreamer.com/).

## Overview

This project implements the PySpark DataSource API (Spark 4.0+) to stream data from Lightstreamer servers into Spark DataFrames. It supports any Lightstreamer adapter (stock quotes, chat, custom adapters).

## Prerequisites

- Python 3.10+
- PySpark 4.0+
- A Lightstreamer server (local or remote)

## Setup

```bash
# Install dependencies
poetry install

# Start a local Lightstreamer server (optional)
cd docker && docker-compose up -d
```

## Usage

```python
from lightstreamer_pyspark import LightstreamerDataSource

# Register the data source
spark.dataSource.register(LightstreamerDataSource)

# Create a streaming DataFrame
df = spark.readStream.format("lightstreamer") \
    .option("server_url", "http://localhost:8080") \
    .option("adapter_set", "DEMO") \
    .option("items", "item1,item2,item3") \
    .option("fields", "stock_name,last_price,time") \
    .option("mode", "MERGE") \
    .load()

# Write to console
query = df.writeStream \
    .format("console") \
    .start()

query.awaitTermination()
```

## Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `server_url` | Yes | - | Lightstreamer server URL |
| `adapter_set` | No | `DEMO` | Adapter set name |
| `items` | Yes | - | Comma-separated item names |
| `fields` | Yes | - | Comma-separated field names |
| `mode` | No | `MERGE` | Subscription mode (MERGE, DISTINCT, RAW, COMMAND) |
| `max_queue_size` | No | `10000` | Maximum buffered messages |
| `batch_size` | No | `100` | Messages per microbatch |

## Running Tests

```bash
# Unit tests only (default)
poetry run pytest

# All tests including integration
poetry run pytest -m ""

# With coverage
poetry run pytest --cov=lightstreamer_pyspark --cov-report=term-missing
```

## Project Structure

```
├── src/
│   └── lightstreamer_pyspark/
│       ├── __init__.py
│       ├── data_source.py          # DataSource + StreamReader
│       └── lightstreamer_client.py # Client wrapper + message queue
├── tests/
│   ├── conftest.py
│   ├── test_lightstreamer_client.py
│   ├── test_integration.py
│   └── test_public_demo.py
├── docker/
│   ├── docker-compose.yml
│   └── Dockerfile.lightstreamer
├── scripts/
│   └── ...
├── examples/
│   └── ...
└── pyproject.toml
```

## License

Apache License 2.0. See [LICENSE](LICENSE).
