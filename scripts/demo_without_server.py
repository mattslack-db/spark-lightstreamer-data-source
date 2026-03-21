#!/usr/bin/env python3
"""
Demo script showing how to use the data source (without a live server).

This demonstrates the API and schema generation without requiring
a running LightStreamer server.
"""

from lightstreamer_pyspark.data_source import LightstreamerDataSource
from pyspark.sql.types import StructType
import json


def main():
    """Demonstrate the data source API."""
    
    print("=" * 70)
    print("LightStreamer PySpark Data Source - Demo")
    print("=" * 70)
    
    # Configuration options
    options = {
        "server_url": "http://localhost:8080",
        "adapter_set": "DEMO",
        "items": "item1,item2,item3",
        "fields": "stock_name,last_price,time,pct_change",
        "mode": "MERGE",
        "batch_size": "100",
    }
    
    print("\n1. Creating data source with options:")
    for key, value in options.items():
        print(f"   {key}: {value}")
    
    # Create data source
    ds = LightstreamerDataSource(options)
    
    print(f"\n2. Data source name: {ds.name()}")
    
    # Get schema
    schema_json = ds.schema()
    schema = StructType.fromJson(json.loads(schema_json))
    
    print("\n3. Generated schema:")
    print(f"   Fields: {len(schema.fields)}")
    for field in schema.fields:
        print(f"   - {field.name}: {field.dataType}")
    
    print("\n4. How to use in PySpark:")
    print("""
    df = spark.readStream \\
        .format("lightstreamer") \\
        .option("server_url", "http://localhost:8080") \\
        .option("adapter_set", "DEMO") \\
        .option("items", "item1,item2,item3") \\
        .option("fields", "stock_name,last_price,time") \\
        .load()
    """)
    
    print("\n5. Configuration options:")
    print("   Required:")
    print("   - server_url: LightStreamer server URL")
    print("   - items: Comma-separated item names")
    print("   - fields: Comma-separated field names")
    print("\n   Optional:")
    print("   - adapter_set: Adapter name (default: DEMO)")
    print("   - mode: Subscription mode (default: MERGE)")
    print("   - batch_size: Messages per batch (default: 100)")
    print("   - max_queue_size: Queue size (default: 10000)")
    print("   - log_level: Logging level (default: INFO)")
    
    print("\n" + "=" * 70)
    print("✅ Data source successfully configured!")
    print("=" * 70)
    
    print("\nNext steps:")
    print("1. Install Docker to run the full example with a live server")
    print("2. Or connect to a remote LightStreamer server")
    print("3. Run: python scripts/simple_example.py (requires server)")


if __name__ == "__main__":
    main()

