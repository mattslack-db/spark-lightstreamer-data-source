# Examples

This directory contains example notebooks and scripts demonstrating how to use the LightStreamer PySpark streaming source.

## Contents

- `basic_usage.ipynb` - Basic usage examples showing how to connect to LightStreamer and process streaming data
- `advanced_patterns.ipynb` - Advanced patterns including aggregations, joins, and complex transformations

## Running the Examples

### Prerequisites

1. Install the package:
```bash
pip install -e .
```

2. Start a LightStreamer server:
```bash
cd docker
docker-compose up -d
```

3. Start Jupyter:
```bash
jupyter notebook
```

4. Open one of the example notebooks and run the cells.

## Example Data

The examples use the LightStreamer demo adapter which simulates stock market data. The demo includes items like:

- `item1`, `item2`, `item3`, etc. - Simulated stock items
- Fields: `stock_name`, `last_price`, `time`, `pct_change`, `bid`, `ask`, `min`, `max`

## Cleaning Up

Stop the LightStreamer server when done:

```bash
cd docker
docker-compose down
```

