"""
PySpark custom streaming data source for Lightstreamer.

Implements the PySpark DataSource API for streaming data from Lightstreamer.
The stream reader maintains a persistent connection across microbatches,
accumulating messages in a thread-safe queue and draining them on each read().
"""

import logging
import time
from typing import List, Dict, Any, Iterator, Tuple

from pyspark.sql.datasource import DataSource, DataSourceStreamReader, InputPartition
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

logger = logging.getLogger(__name__)


class LightstreamerDataSource(DataSource):
    """
    Custom PySpark data source for Lightstreamer streaming data.

    Usage:
        spark.dataSource.register(LightstreamerDataSource)

        df = spark.readStream.format("lightstreamer") \\
            .option("server_url", "http://localhost:8080") \\
            .option("adapter_set", "DEMO") \\
            .option("items", "item1,item2,item3") \\
            .option("fields", "field1,field2,field3") \\
            .option("mode", "MERGE") \\
            .load()
    """

    @classmethod
    def name(cls) -> str:
        return "lightstreamer"

    def schema(self) -> StructType:
        """Return the schema derived from the configured fields."""
        fields_str = self.options.get("fields", "")
        if not fields_str:
            raise ValueError("'fields' option must be provided")

        field_names = [f.strip() for f in fields_str.split(",")]

        struct_fields = [StructField(name, StringType(), True) for name in field_names]
        struct_fields.append(StructField("item_name", StringType(), True))
        struct_fields.append(StructField("item_pos", IntegerType(), True))

        return StructType(struct_fields)

    def streamReader(self, schema: StructType) -> "LightstreamerStreamReader":
        return LightstreamerStreamReader(self.options, schema)


class LightstreamerInputPartition(InputPartition):
    """Single partition carrying connection configuration."""

    def __init__(self, partition_id: int):
        self.partition_id = partition_id


class LightstreamerStreamReader(DataSourceStreamReader):
    """
    Stream reader that maintains a persistent Lightstreamer connection.

    The connection and subscription are established on first use and kept alive
    across microbatches. Messages accumulate in a thread-safe queue between
    calls to read(). The offset tracks how many messages have been consumed.
    """

    def __init__(self, options: Dict[str, str], schema: StructType):
        self._options = options
        self._schema = schema
        self._committed_offset = 0
        self._current_offset = 0

        # Validate required options
        required = ["server_url", "items", "fields"]
        missing = [opt for opt in required if opt not in self._options]
        if missing:
            raise ValueError(f"Missing required options: {', '.join(missing)}")

        # Extract configuration
        self._server_url = self._options["server_url"]
        self._adapter_set = self._options.get("adapter_set", "DEMO")
        self._items = [item.strip() for item in self._options["items"].split(",")]
        self._fields = [field.strip() for field in self._options["fields"].split(",")]
        self._mode = self._options.get("mode", "MERGE")
        self._max_queue_size = int(self._options.get("max_queue_size", "10000"))
        self._batch_size = int(self._options.get("batch_size", "100"))

        # Connection state — lazily initialised
        self._client_manager = None
        self._message_queue = None
        self._buffer: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    def _ensure_connected(self):
        """Lazily connect and subscribe on first use."""
        if self._client_manager is not None:
            return

        from .lightstreamer_client import LightstreamerClientManager

        self._client_manager = LightstreamerClientManager(
            server_url=self._server_url,
            adapter_set=self._adapter_set,
        )
        self._client_manager.connect()
        self._message_queue = self._client_manager.subscribe(
            items=self._items,
            fields=self._fields,
            mode=self._mode,
            max_queue_size=self._max_queue_size,
        )
        logger.info("Lightstreamer connection established")

    # ------------------------------------------------------------------
    # DataSourceStreamReader API
    # ------------------------------------------------------------------

    def initialOffset(self) -> Dict[str, int]:
        return {"offset": 0}

    def latestOffset(self) -> Dict[str, int]:
        """Drain the message queue into the internal buffer and advance offset."""
        self._ensure_connected()

        # Drain all currently available messages into the buffer
        messages = self._message_queue.get_batch(
            max_items=self._batch_size,
            timeout=0.5,
        )
        self._buffer.extend(messages)
        self._current_offset = self._committed_offset + len(self._buffer)

        return {"offset": self._current_offset}

    def partitions(self, start: Dict[str, int], end: Dict[str, int]) -> List[LightstreamerInputPartition]:
        return [LightstreamerInputPartition(partition_id=0)]

    def read(self, partition: InputPartition) -> Iterator[Tuple]:
        """Yield buffered messages as rows and clear the buffer."""
        for message in self._buffer:
            row = []
            for field in self._fields:
                row.append(message.get(field))
            row.append(message.get("item_name"))
            row.append(message.get("item_pos"))
            yield tuple(row)

        self._buffer.clear()

    def commit(self, end: Dict[str, int]):
        self._committed_offset = end.get("offset", self._committed_offset)
        logger.debug(f"Committed offset: {self._committed_offset}")

    def stop(self):
        """Disconnect from Lightstreamer."""
        if self._client_manager:
            self._client_manager.disconnect()
            self._client_manager = None
            logger.info("Lightstreamer connection closed")
