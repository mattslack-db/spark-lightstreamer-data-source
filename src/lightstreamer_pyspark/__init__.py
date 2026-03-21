"""
Lightstreamer PySpark Streaming Data Source

A custom PySpark streaming data source for consuming data from Lightstreamer.
"""

from .data_source import LightstreamerDataSource, LightstreamerStreamReader

__version__ = "0.1.0"
__all__ = ["LightstreamerDataSource", "LightstreamerStreamReader"]
