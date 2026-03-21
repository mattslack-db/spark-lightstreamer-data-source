"""
Lightstreamer client wrapper for PySpark integration.

Based on: https://github.com/Lightstreamer/Lightstreamer-example-StockList-client-python
"""

import threading
import queue
import logging
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


class LightstreamerMessageQueue:
    """Thread-safe queue for collecting messages from Lightstreamer subscriptions."""

    def __init__(self, max_size: int = 10000):
        self.queue = queue.Queue(maxsize=max_size)
        self._stopped = threading.Event()

    def put(self, item: Dict[str, Any], block: bool = True, timeout: Optional[float] = None):
        """Add an item to the queue."""
        if self._stopped.is_set():
            return
        try:
            self.queue.put(item, block=block, timeout=timeout)
        except queue.Full:
            logger.warning("Message queue is full, dropping message")

    def get(self, block: bool = True, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Get an item from the queue."""
        try:
            return self.queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def get_batch(self, max_items: int = 100, timeout: float = 1.0) -> List[Dict[str, Any]]:
        """Get a batch of items from the queue."""
        items = []
        try:
            first_item = self.queue.get(block=True, timeout=timeout)
            if first_item is not None:
                items.append(first_item)

            while len(items) < max_items:
                try:
                    item = self.queue.get(block=False)
                    if item is not None:
                        items.append(item)
                except queue.Empty:
                    break
        except queue.Empty:
            pass

        return items

    def stop(self):
        """Stop accepting new messages."""
        self._stopped.set()

    def is_stopped(self) -> bool:
        return self._stopped.is_set()

    def size(self) -> int:
        return self.queue.qsize()


class LightstreamerSubscriptionListener:
    """Listener for Lightstreamer subscription events."""

    def __init__(self, message_queue: LightstreamerMessageQueue, fields: List[str]):
        self.message_queue = message_queue
        self.fields = fields

    def onItemUpdate(self, update):
        """Called when an item update is received."""
        try:
            message = {}
            for field in self.fields:
                message[field] = update.getValue(field)

            message["item_name"] = update.getItemName()
            message["item_pos"] = update.getItemPos()

            self.message_queue.put(message, block=False)
        except Exception as e:
            logger.error(f"Error processing item update: {e}", exc_info=True)

    def onSubscriptionError(self, code, message):
        logger.error(f"Subscription error {code}: {message}")

    def onListenStart(self):
        logger.info("Subscription started")

    def onListenEnd(self):
        logger.info("Subscription ended")


class LightstreamerClientManager:
    """Manages Lightstreamer client connection and subscriptions."""

    def __init__(self, server_url: str, adapter_set: str = "DEMO", log_level: str = "INFO"):
        self.server_url = server_url
        self.adapter_set = adapter_set
        self.client = None
        self.subscription = None
        self.message_queue = None
        self._connected = False

    def connect(self):
        """Connect to the Lightstreamer server."""
        if self._connected:
            logger.warning("Already connected")
            return

        from lightstreamer.client import LightstreamerClient

        self.client = LightstreamerClient(self.server_url, self.adapter_set)
        self.client.connect()
        self._connected = True
        logger.info(f"Connected to Lightstreamer at {self.server_url}")

    def subscribe(
        self,
        items: List[str],
        fields: List[str],
        mode: str = "MERGE",
        max_queue_size: int = 10000,
    ) -> LightstreamerMessageQueue:
        """Subscribe to Lightstreamer items and return the message queue."""
        if not self._connected:
            raise RuntimeError("Not connected to Lightstreamer")

        from lightstreamer.client import Subscription

        self.message_queue = LightstreamerMessageQueue(max_size=max_queue_size)

        self.subscription = Subscription(mode, items, fields)
        listener = LightstreamerSubscriptionListener(self.message_queue, fields)
        self.subscription.addListener(listener)

        self.client.subscribe(self.subscription)
        logger.info(f"Subscribed to items: {items}, fields: {fields}")

        return self.message_queue

    def disconnect(self):
        """Disconnect from the Lightstreamer server."""
        if self.subscription and self.client:
            try:
                self.client.unsubscribe(self.subscription)
            except Exception as e:
                logger.warning(f"Error unsubscribing: {e}")

        if self.message_queue:
            self.message_queue.stop()

        if self.client and self._connected:
            try:
                self.client.disconnect()
                self._connected = False
                logger.info("Disconnected from Lightstreamer")
            except Exception as e:
                logger.warning(f"Error disconnecting: {e}")

    def is_connected(self) -> bool:
        return self._connected

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
