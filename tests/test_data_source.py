"""Unit tests for the Lightstreamer DataSource and StreamReader."""

import pytest
from pyspark.sql.types import StructType


class TestLightstreamerDataSourceUnit:
    """Unit tests for the data source without requiring a server."""

    def test_data_source_name(self):
        from lightstreamer_pyspark.data_source import LightstreamerDataSource
        assert LightstreamerDataSource.name() == "lightstreamer"

    def test_schema_from_fields(self):
        from lightstreamer_pyspark.data_source import LightstreamerDataSource

        ds = LightstreamerDataSource({"fields": "field1,field2,field3"})
        schema = ds.schema()

        assert isinstance(schema, StructType)
        field_names = [f.name for f in schema.fields]
        assert "field1" in field_names
        assert "field2" in field_names
        assert "field3" in field_names
        assert "item_name" in field_names
        assert "item_pos" in field_names

    def test_missing_fields_raises_error(self):
        from lightstreamer_pyspark.data_source import LightstreamerDataSource

        ds = LightstreamerDataSource({})
        with pytest.raises(ValueError, match="fields"):
            ds.schema()

    def test_stream_reader_validation(self):
        from lightstreamer_pyspark.data_source import LightstreamerStreamReader

        with pytest.raises(ValueError, match="Missing required options"):
            LightstreamerStreamReader({"fields": "field1"}, StructType([]))

    def test_stream_reader_initial_offset(self):
        from lightstreamer_pyspark.data_source import LightstreamerStreamReader

        reader = LightstreamerStreamReader(
            {
                "server_url": "http://localhost:8080",
                "items": "item1",
                "fields": "field1",
            },
            StructType([]),
        )
        assert reader.initialOffset() == {"offset": 0}

    def test_stream_reader_partitions(self):
        from lightstreamer_pyspark.data_source import LightstreamerStreamReader

        reader = LightstreamerStreamReader(
            {
                "server_url": "http://localhost:8080",
                "items": "item1",
                "fields": "field1",
            },
            StructType([]),
        )
        parts = reader.partitions({"offset": 0}, {"offset": 10})
        assert len(parts) == 1
        assert parts[0].partition_id == 0
