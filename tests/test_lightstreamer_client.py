"""
Unit tests for LightStreamer client wrapper.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from lightstreamer_pyspark.lightstreamer_client import (
    LightstreamerMessageQueue,
    LightstreamerSubscriptionListener,
    LightstreamerClientManager
)


class TestLightstreamerMessageQueue:
    """Tests for LightstreamerMessageQueue."""
    
    def test_queue_put_get(self):
        """Test basic put and get operations."""
        queue = LightstreamerMessageQueue(max_size=10)
        
        message = {"field1": "value1", "field2": "value2"}
        queue.put(message)
        
        retrieved = queue.get(timeout=1.0)
        assert retrieved == message
    
    def test_queue_get_batch(self):
        """Test batch retrieval."""
        queue = LightstreamerMessageQueue(max_size=100)
        
        # Add multiple messages
        messages = [{"id": i, "value": f"val{i}"} for i in range(10)]
        for msg in messages:
            queue.put(msg)
        
        # Retrieve batch
        batch = queue.get_batch(max_items=5, timeout=1.0)
        assert len(batch) == 5
        assert batch[0]["id"] == 0
        assert batch[4]["id"] == 4
    
    def test_queue_stop(self):
        """Test queue stop functionality."""
        queue = LightstreamerMessageQueue(max_size=10)
        
        queue.stop()
        assert queue.is_stopped()
        
        # After stop, put should not raise but message won't be added
        queue.put({"test": "data"})
        assert queue.size() == 0


class TestLightstreamerSubscriptionListener:
    """Tests for LightstreamerSubscriptionListener."""
    
    def test_on_item_update(self):
        """Test handling of item updates."""
        queue = LightstreamerMessageQueue(max_size=10)
        fields = ["field1", "field2"]
        listener = LightstreamerSubscriptionListener(queue, fields)
        
        # Mock update object
        update = Mock()
        update.getValue = Mock(side_effect=lambda f: f"value_{f}")
        update.getItemName = Mock(return_value="item1")
        update.getItemPos = Mock(return_value=1)
        
        # Process update
        listener.onItemUpdate(update)
        
        # Check message in queue
        message = queue.get(timeout=1.0)
        assert message is not None
        assert message["field1"] == "value_field1"
        assert message["field2"] == "value_field2"
        assert message["item_name"] == "item1"
        assert message["item_pos"] == 1


class TestLightstreamerClientManager:
    """Tests for LightstreamerClientManager."""
    
    @patch('lightstreamer.client.LightstreamerClient')
    def test_connect(self, mock_client_class):
        """Test connection to LightStreamer."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        manager = LightstreamerClientManager(
            server_url="http://localhost:8080",
            adapter_set="DEMO"
        )
        
        manager.connect()
        
        assert manager.is_connected()
        mock_client.connect.assert_called_once()
    
    @patch('lightstreamer.client.LightstreamerClient')
    @patch('lightstreamer.client.Subscription')
    def test_subscribe(self, mock_subscription_class, mock_client_class):
        """Test subscription to items."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_subscription = Mock()
        mock_subscription_class.return_value = mock_subscription
        
        manager = LightstreamerClientManager(
            server_url="http://localhost:8080",
            adapter_set="DEMO"
        )
        manager.connect()
        
        items = ["item1", "item2"]
        fields = ["field1", "field2"]
        message_queue = manager.subscribe(items, fields)
        
        assert message_queue is not None
        mock_subscription_class.assert_called_once_with("MERGE", items, fields)
        mock_subscription.addListener.assert_called_once()
        mock_client.subscribe.assert_called_once_with(mock_subscription)
    
    @patch('lightstreamer.client.LightstreamerClient')
    def test_disconnect(self, mock_client_class):
        """Test disconnection from LightStreamer."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        manager = LightstreamerClientManager(
            server_url="http://localhost:8080",
            adapter_set="DEMO"
        )
        manager.connect()
        manager.disconnect()
        
        assert not manager.is_connected()
        mock_client.disconnect.assert_called_once()
    
    @patch('lightstreamer.client.LightstreamerClient')
    def test_context_manager(self, mock_client_class):
        """Test context manager functionality."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        with LightstreamerClientManager(
            server_url="http://localhost:8080",
            adapter_set="DEMO"
        ) as manager:
            assert manager.is_connected()
        
        mock_client.disconnect.assert_called_once()

