"""
Integration tests for Lightstreamer PySpark source.

These tests require a running Lightstreamer server.
Use docker-compose up -d to start one locally, or set LIGHTSTREAMER_SERVER.
"""

import pytest
import time
import os
import tempfile


LIGHTSTREAMER_SERVER = os.environ.get("LIGHTSTREAMER_SERVER", "http://localhost:8080")

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.environ.get("SKIP_INTEGRATION") == "1",
        reason="Skipping integration tests (SKIP_INTEGRATION=1)",
    ),
]


@pytest.fixture(scope="module")
def server_url():
    """Return the Lightstreamer server URL, verifying it's reachable."""
    import urllib.request
    try:
        urllib.request.urlopen(LIGHTSTREAMER_SERVER, timeout=5)
    except Exception:
        pytest.skip(f"Lightstreamer server not reachable at {LIGHTSTREAMER_SERVER}")
    return LIGHTSTREAMER_SERVER


def test_lightstreamer_client_integration(server_url):
    """Test real connection to Lightstreamer server."""
    from lightstreamer_pyspark.lightstreamer_client import LightstreamerClientManager

    with LightstreamerClientManager(
        server_url=server_url,
        adapter_set="DEMO",
    ) as manager:
        assert manager.is_connected()

        items = ["item1", "item2"]
        fields = ["stock_name", "last_price", "time"]
        queue = manager.subscribe(items, fields, mode="MERGE")

        time.sleep(5)
        messages = queue.get_batch(max_items=50, timeout=2.0)

        print(f"\nIntegration test: received {len(messages)} messages from {server_url}")
        if messages:
            for msg in messages[:3]:
                print(f"  {msg.get('item_name')}: {msg.get('stock_name')} @ {msg.get('last_price')}")
