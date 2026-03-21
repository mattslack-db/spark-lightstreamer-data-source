
Create a pyspark custom streaming source that consumes data from LightStreamer, in the same way as is done in this example: https://github.com/Lightstreamer/Lightstreamer-example-StockList-client-python.

For examples of python custom streaming sources, use the following web pages:
- https://docs.databricks.com/aws/en/pyspark/datasources
- https://github.com/allisonwang-db/pyspark-data-sources/tree/master/pyspark_datasources
- https://community.databricks.com/t5/technical-blog/enhancing-the-new-pyspark-custom-data-sources-streaming-api/ba-p/75538
- https://github.com/alexott/cyber-spark-data-connectors
- https://github.com/dmoore247/PythonDataSources
- https://github.com/jiteshsoni/ethereum-streaming-pipeline/blob/main/ethereum-custom-reader-dev.ipynb
- https://github.com/databricks-industry-solutions/python-data-sources/tree/main/mqtt/src/python_datasource_connectors

Integration test should be created that spin up a local LightStreamer instance and simulate sending some data which is then read by the pyspark custom streaming source into a table.
