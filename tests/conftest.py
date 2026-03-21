"""Pytest configuration and shared fixtures."""

import os
import sys
import time
from pathlib import Path

import pytest
from pyspark.sql import SparkSession

# Ensure the package is importable when running pytest from repo root.
_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# Ensure Spark workers use the same Python as the driver
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


@pytest.fixture(autouse=True)
def _mock_lightstreamer_for_unit_tests(request):
    """Mock lightstreamer SDK for unit tests so imports don't fail."""
    from unittest.mock import MagicMock

    if "integration" in request.keywords:
        yield
        return

    modules_to_mock = [
        "lightstreamer",
        "lightstreamer.client",
    ]
    originals = {}
    for key in modules_to_mock:
        if key not in sys.modules:
            originals[key] = None
            sys.modules[key] = MagicMock()
        else:
            originals[key] = sys.modules[key]
    try:
        yield
    finally:
        for key, val in originals.items():
            if val is None and key in sys.modules:
                del sys.modules[key]
            elif val is not None:
                sys.modules[key] = val


@pytest.fixture(scope="session")
def spark():
    """Create a Spark session for testing."""
    spark = SparkSession.builder \
        .appName("lightstreamer-tests") \
        .master("local[2]") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()
    yield spark
    for q in spark.streams.active:
        try:
            q.stop()
        except Exception:
            pass
    time.sleep(1)
    spark.stop()


@pytest.fixture
def basic_options():
    """Basic connection options for testing."""
    return {
        "server_url": "http://localhost:8080",
        "adapter_set": "DEMO",
        "items": "item1,item2,item3",
        "fields": "stock_name,last_price,time",
        "mode": "MERGE",
    }
