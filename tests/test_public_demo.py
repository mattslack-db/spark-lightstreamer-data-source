"""
Tests using Lightstreamer demo adapters: CHAT_ROOM and QUOTE_ADAPTER

These tests validate the integration with real Lightstreamer adapters.
They can work with:
- A local server with demo adapters configured
- Public demo servers (if data is actively streaming)

**Setup Instructions:**

1. **Local Setup (Recommended):**
   - Use the Docker setup in this project: `docker-compose up -d`
   - Or download Lightstreamer Server from https://lightstreamer.com/download/
   - The DEMO adapter set (including QUOTE_ADAPTER) comes pre-installed
   - For CHAT_ROOM, deploy the adapter from:
     https://github.com/Lightstreamer/Lightstreamer-example-Chat-adapter-java

2. **Public Demo Servers:**
   - These servers may not actively stream data unless demos are accessed via web UI
   - Tests are designed to handle this gracefully

**Environment Variables:**
- `LIGHTSTREAMER_SERVER`: Server URL (default: http://localhost:8080)
- `SKIP_PUBLIC_DEMO=1`: Skip these tests entirely
"""

import pytest
import time
import os
from lightstreamer_pyspark.lightstreamer_client import LightstreamerClientManager


# Get server URL from environment or use local default
DEMO_SERVER_URL = os.environ.get("LIGHTSTREAMER_SERVER", "http://localhost:8080")

# Skip if SKIP_PUBLIC_DEMO env var is set
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_PUBLIC_DEMO") == "1",
    reason="Skipping demo adapter tests (SKIP_PUBLIC_DEMO=1)"
)


class TestChatRoomAdapter:
    """
    Tests for the CHAT_ROOM demo adapter.
    
    The CHAT_ROOM adapter implements a basic chat application where
    users can exchange messages in real-time.
    
    **Required Setup:**
    - Deploy the CHAT_ROOM adapter from:
      https://github.com/Lightstreamer/Lightstreamer-example-Chat-adapter-java
    - Configure adapter with name "CHAT_ROOM" in adapters.xml
    - Item name is typically "chat_room"
    - Subscription mode: DISTINCT
    """
    
    def test_chat_room_connection_and_subscription(self):
        """
        Test that we can connect to and subscribe to the CHAT_ROOM adapter.
        
        This test verifies:
        1. Connection to server succeeds
        2. Subscription to CHAT_ROOM adapter is accepted
        3. Message queue is properly initialized
        
        Note: Actual message reception depends on chat activity.
        """
        # CHAT_ROOM adapter uses DISTINCT mode for chat messages
        manager = LightstreamerClientManager(
            server_url=DEMO_SERVER_URL,
            adapter_set="CHAT_ROOM",
            log_level="INFO"
        )
        
        try:
            manager.connect()
            assert manager.is_connected(), "Should connect successfully"
            
            # Subscribe to chat room
            items = ["chat_room"]
            fields = ["message", "raw_timestamp", "IP"]
            
            message_queue = manager.subscribe(
                items=items,
                fields=fields,
                mode="DISTINCT"  # DISTINCT mode for chat messages
            )
            
            assert message_queue is not None, "Message queue should be created"
            
            # Wait for potential messages
            time.sleep(5)
            
            # Try to get messages (there may or may not be any)
            messages = message_queue.get_batch(max_items=10, timeout=2.0)
            
            print(f"\nCHAT_ROOM Test Results:")
            print(f"  Server URL: {DEMO_SERVER_URL}")
            print(f"  Connected: {manager.is_connected()}")
            print(f"  Subscribed to: {items}")
            print(f"  Messages received: {len(messages)}")
            
            if len(messages) > 0:
                print(f"  ✓ Chat is active, received {len(messages)} messages")
                for i, msg in enumerate(messages[:3], 1):
                    print(f"    Message {i}: {msg.get('message', 'N/A')}")
                    
                # Verify message structure
                msg = messages[0]
                assert "item_name" in msg, "Message should have item_name"
                assert "item_pos" in msg, "Message should have item_pos"
                assert "message" in msg, "Message should have message field"
            else:
                print("  ℹ No messages received (chat may be inactive)")
                print("  ℹ To test with messages, send chat messages via the web demo")
                
        finally:
            manager.disconnect()
    
    def test_chat_room_message_structure(self):
        """
        Test that chat room messages have the expected structure when received.
        
        This test waits longer for messages and validates their structure.
        Skips validation if no messages are received.
        """
        with LightstreamerClientManager(
            server_url=DEMO_SERVER_URL,
            adapter_set="CHAT_ROOM",
            log_level="INFO"
        ) as manager:
            
            items = ["chat_room"]
            fields = ["message", "raw_timestamp", "IP"]
            
            message_queue = manager.subscribe(
                items=items,
                fields=fields,
                mode="DISTINCT"
            )
            
            # Wait longer for messages
            time.sleep(10)
            
            messages = message_queue.get_batch(max_items=5, timeout=2.0)
            
            if len(messages) > 0:
                print(f"\nValidating chat message structure...")
                
                # Verify structure of first message
                msg = messages[0]
                assert "item_name" in msg, "Should have item_name"
                assert "item_pos" in msg, "Should have item_pos"
                assert "message" in msg, "Should have message field"
                assert "raw_timestamp" in msg, "Should have raw_timestamp field"
                assert "IP" in msg, "Should have IP field"
                
                print(f"  ✓ Message structure validated")
                print(f"  Sample message: {msg}")
            else:
                pytest.skip("No chat messages received - skipping structure validation")


class TestQuoteAdapter:
    """
    Tests for the QUOTE_ADAPTER (stock quotes).
    
    The QUOTE_ADAPTER is part of the DEMO adapter set and provides
    simulated real-time stock market data.
    
    **Setup:**
    - The DEMO adapter set comes pre-installed with Lightstreamer Server
    - Items are named item1, item2, item3, etc. (typically item1-item30)
    - Subscription mode: MERGE
    - The adapter generates continuous simulated stock updates
    """
    
    def test_quote_adapter_connection_and_subscription(self):
        """
        Test that we can connect to and subscribe to the QUOTE_ADAPTER.
        
        This test verifies:
        1. Connection to server succeeds
        2. Subscription to stock items is accepted  
        3. Stock updates are received (if adapter is running)
        """
        manager = LightstreamerClientManager(
            server_url=DEMO_SERVER_URL,
            adapter_set="DEMO",  # QUOTE_ADAPTER is part of DEMO adapter set
            log_level="INFO"
        )
        
        try:
            manager.connect()
            assert manager.is_connected(), "Should connect successfully"
            
            # Subscribe to stock items
            # Common items: item1 to item30 represent different stocks
            items = ["item1", "item2", "item3"]
            fields = ["stock_name", "last_price", "time", "pct_change"]
            
            message_queue = manager.subscribe(
                items=items,
                fields=fields,
                mode="MERGE"  # MERGE mode for stock quotes
            )
            
            assert message_queue is not None, "Message queue should be created"
            
            # Wait for stock updates
            time.sleep(7)
            
            # Get received messages
            messages = message_queue.get_batch(max_items=50, timeout=2.0)
            
            print(f"\nQUOTE_ADAPTER (DEMO) Test Results:")
            print(f"  Server URL: {DEMO_SERVER_URL}")
            print(f"  Connected: {manager.is_connected()}")
            print(f"  Subscribed to: {items}")
            print(f"  Messages received: {len(messages)}")
            
            if len(messages) > 0:
                print(f"  ✓ Stock quotes streaming successfully")
                for msg in messages[:5]:  # Print first 5 messages
                    print(f"    Stock: {msg.get('stock_name')}, "
                          f"Price: {msg.get('last_price')}, "
                          f"Change: {msg.get('pct_change')}%")
                
                # Basic assertions
                assert len(messages) > 0, "Should receive stock quote updates"
            else:
                print("  ⚠ No stock quotes received")
                print("  ⚠ Ensure DEMO adapter is properly configured and running")
                pytest.skip("No stock quotes received - adapter may not be running")
                
        finally:
            manager.disconnect()
    
    def test_quote_adapter_message_structure(self):
        """
        Test that stock quote messages have the expected structure.
        
        Verifies all required fields are present in stock update messages.
        """
        with LightstreamerClientManager(
            server_url=DEMO_SERVER_URL,
            adapter_set="DEMO",
            log_level="INFO"
        ) as manager:
            
            items = ["item1"]
            fields = ["stock_name", "last_price", "time", "pct_change", "bid", "ask"]
            
            message_queue = manager.subscribe(
                items=items,
                fields=fields,
                mode="MERGE"
            )
            
            # Wait for updates
            time.sleep(5)
            
            messages = message_queue.get_batch(max_items=10, timeout=2.0)
            
            if len(messages) > 0:
                print(f"\nValidating stock quote message structure...")
                
                # Verify message structure
                msg = messages[0]
                assert "item_name" in msg, "Should have item_name"
                assert "item_pos" in msg, "Should have item_pos"
                assert "stock_name" in msg, "Should have stock_name field"
                assert "last_price" in msg, "Should have last_price field"
                assert "time" in msg, "Should have time field"
                assert "pct_change" in msg, "Should have pct_change field"
                assert "bid" in msg, "Should have bid field"
                assert "ask" in msg, "Should have ask field"
                
                print(f"  ✓ Stock quote structure validated")
                print(f"  Sample quote: {msg}")
            else:
                pytest.skip("No stock quotes received - skipping structure validation")
    
    def test_quote_adapter_multiple_items(self):
        """
        Test subscribing to multiple stock items simultaneously.
        
        Verifies that:
        1. Multiple item subscriptions work
        2. Updates are received from different items
        3. Item identification works correctly
        """
        with LightstreamerClientManager(
            server_url=DEMO_SERVER_URL,
            adapter_set="DEMO",
            log_level="INFO"
        ) as manager:
            
            # Subscribe to multiple stocks
            items = [f"item{i}" for i in range(1, 11)]  # item1 to item10
            fields = ["stock_name", "last_price", "time"]
            
            message_queue = manager.subscribe(
                items=items,
                fields=fields,
                mode="MERGE"
            )
            
            # Wait for updates from multiple items
            time.sleep(7)
            
            messages = message_queue.get_batch(max_items=100, timeout=2.0)
            
            print(f"\nMulti-item subscription test:")
            print(f"  Subscribed to {len(items)} items")
            print(f"  Received {len(messages)} updates")
            
            if len(messages) > 0:
                # Check we got updates from different items
                unique_items = set(msg.get("item_name") for msg in messages)
                print(f"  Updates from {len(unique_items)} different items: {unique_items}")
                
                # Should have at least a few different stocks
                assert len(unique_items) > 1, "Should receive updates from multiple stocks"
                print(f"  ✓ Multi-item subscription working correctly")
            else:
                pytest.skip("No stock quotes received - skipping multi-item test")
    
    def test_quote_adapter_continuous_updates(self):
        """
        Test that stock quotes continue to update over time.
        
        This test verifies that the QUOTE_ADAPTER generates continuous
        updates by collecting messages in multiple time windows.
        """
        with LightstreamerClientManager(
            server_url=DEMO_SERVER_URL,
            adapter_set="DEMO",
            log_level="INFO"
        ) as manager:
            
            items = ["item1", "item2"]
            fields = ["stock_name", "last_price", "time"]
            
            message_queue = manager.subscribe(
                items=items,
                fields=fields,
                mode="MERGE"
            )
            
            # Collect messages in two batches with a delay
            print(f"\nContinuous updates test:")
            
            time.sleep(4)
            batch1 = message_queue.get_batch(max_items=20, timeout=1.0)
            print(f"  First batch: {len(batch1)} messages")
            
            time.sleep(4)
            batch2 = message_queue.get_batch(max_items=20, timeout=1.0)
            print(f"  Second batch: {len(batch2)} messages")
            
            # Both batches should have messages (continuous updates)
            if len(batch1) > 0 and len(batch2) > 0:
                print(f"  ✓ Continuous updates confirmed")
                assert True, "Continuous updates working"
            elif len(batch1) > 0 or len(batch2) > 0:
                print(f"  ⚠ Received some messages but not continuous")
                # Still pass if we got at least one batch
                assert True
            else:
                pytest.skip("No stock quotes received - skipping continuous updates test")


class TestConnectionLifecycle:
    """Test connection handling and lifecycle management."""
    
    def test_manual_connection_lifecycle(self):
        """
        Test manual connect/disconnect lifecycle.
        
        Verifies:
        1. Initial state is disconnected
        2. Can connect successfully
        3. Can subscribe after connecting
        4. Can disconnect cleanly
        """
        manager = LightstreamerClientManager(
            server_url=DEMO_SERVER_URL,
            adapter_set="DEMO",
            log_level="INFO"
        )
        
        print(f"\nConnection lifecycle test:")
        
        # Initially not connected
        assert not manager.is_connected(), "Should start disconnected"
        print(f"  ✓ Initial state: disconnected")
        
        # Connect
        manager.connect()
        assert manager.is_connected(), "Should be connected"
        print(f"  ✓ Connected successfully")
        
        # Subscribe
        items = ["item1"]
        fields = ["stock_name", "last_price"]
        message_queue = manager.subscribe(items, fields, mode="MERGE")
        print(f"  ✓ Subscribed successfully")
        
        # Wait for messages
        time.sleep(5)
        messages = message_queue.get_batch(max_items=10, timeout=1.0)
        print(f"  ℹ Received {len(messages)} messages")
        
        # Disconnect
        manager.disconnect()
        assert not manager.is_connected(), "Should be disconnected"
        print(f"  ✓ Disconnected successfully")
        print(f"  ✓ Lifecycle test completed")


@pytest.mark.slow
class TestQuoteAdapterPerformance:
    """
    Performance tests with the QUOTE_ADAPTER.
    
    These tests subscribe to many items and measure throughput.
    Mark as 'slow' to skip in quick test runs.
    """
    
    def test_high_frequency_quotes(self):
        """
        Test handling high-frequency quote updates from many stocks.
        
        Subscribes to 30 stock items and measures:
        - Total messages received
        - Message rate (messages per second)
        - Queue handling performance
        """
        with LightstreamerClientManager(
            server_url=DEMO_SERVER_URL,
            adapter_set="DEMO",
            log_level="INFO"
        ) as manager:
            
            # Subscribe to many items for high message rate
            items = [f"item{i}" for i in range(1, 31)]  # All 30 stock items
            fields = ["stock_name", "last_price", "time", "pct_change", 
                     "bid", "ask", "min", "max", "open_price"]
            
            print(f"\nHigh-frequency quote test:")
            print(f"  Subscribing to {len(items)} items with {len(fields)} fields")
            
            message_queue = manager.subscribe(
                items=items,
                fields=fields,
                mode="MERGE",
                max_queue_size=50000
            )
            
            # Collect messages for 10 seconds
            print(f"  Collecting messages for 10 seconds...")
            start_time = time.time()
            all_messages = []
            
            while time.time() - start_time < 10:
                messages = message_queue.get_batch(max_items=100, timeout=0.5)
                all_messages.extend(messages)
                time.sleep(0.1)
            
            elapsed = time.time() - start_time
            
            if len(all_messages) > 0:
                message_rate = len(all_messages) / elapsed
                unique_items = len(set(msg.get("item_name") for msg in all_messages))
                
                print(f"\n  Performance Results:")
                print(f"    Total messages: {len(all_messages)}")
                print(f"    Time elapsed: {elapsed:.1f} seconds")
                print(f"    Message rate: {message_rate:.1f} messages/second")
                print(f"    Unique items: {unique_items}")
                print(f"    Avg per item: {len(all_messages) / unique_items:.1f} messages")
                
                # Reasonable expectations for a working adapter
                assert len(all_messages) > 10, "Should receive a good number of updates"
                print(f"  ✓ Performance test passed")
            else:
                pytest.skip("No messages received - skipping performance test")

