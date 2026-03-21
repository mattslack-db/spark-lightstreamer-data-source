#!/usr/bin/env python3
"""
Quick script to test LightStreamer connection.

This script verifies that:
1. LightStreamer server is accessible
2. The client can connect and subscribe
3. Data is being received
"""

import sys
import time
from lightstreamer_pyspark.lightstreamer_client import LightstreamerClientManager


def test_connection(server_url="http://localhost:8080", timeout=10):
    """Test connection to LightStreamer server."""
    
    print(f"Testing connection to {server_url}...")
    
    try:
        # Create client manager
        with LightstreamerClientManager(
            server_url=server_url,
            adapter_set="DEMO",
            log_level="INFO"
        ) as manager:
            print("✓ Connected to LightStreamer server")
            
            # Subscribe to items
            print("\nSubscribing to items...")
            message_queue = manager.subscribe(
                items=["item1", "item2", "item3"],
                fields=["stock_name", "last_price", "time"],
                mode="MERGE"
            )
            print("✓ Subscribed successfully")
            
            # Wait for some messages
            print(f"\nWaiting {timeout} seconds for data...")
            start_time = time.time()
            message_count = 0
            
            while time.time() - start_time < timeout:
                messages = message_queue.get_batch(max_items=10, timeout=1.0)
                if messages:
                    message_count += len(messages)
                    print(f"  Received {len(messages)} messages (total: {message_count})")
                    
                    # Print first message as sample
                    if message_count == len(messages):
                        print(f"  Sample: {messages[0]}")
            
            if message_count > 0:
                print(f"\n✓ Successfully received {message_count} messages")
                print("\n✅ Connection test PASSED")
                return True
            else:
                print("\n✗ No messages received")
                print("\n❌ Connection test FAILED")
                return False
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\n❌ Connection test FAILED")
        return False


def main():
    """Main entry point."""
    
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    print("=" * 60)
    print("LightStreamer Connection Test")
    print("=" * 60)
    
    success = test_connection(server_url, timeout)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

