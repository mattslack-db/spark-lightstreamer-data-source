#!/usr/bin/env python3
"""
Simple example of using LightStreamer PySpark source.

This script demonstrates the basic usage pattern.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp
import time


def main():
    """Run a simple streaming example."""
    
    print("Starting LightStreamer PySpark example...")
    
    # Create Spark session
    spark = SparkSession.builder \
        .appName("LightStreamerSimpleExample") \
        .master("local[2]") \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    print("\nConnecting to LightStreamer...")
    
    # Create streaming DataFrame
    df = spark.readStream \
        .format("lightstreamer") \
        .option("server_url", "http://localhost:8080") \
        .option("adapter_set", "DEMO") \
        .option("items", "item1,item2,item3") \
        .option("fields", "stock_name,last_price,time") \
        .option("batch_size", "50") \
        .load()
    
    print("✓ Connected to LightStreamer")
    print("\nSchema:")
    df.printSchema()
    
    # Process the stream
    processed_df = df \
        .withColumn("last_price", col("last_price").cast("double")) \
        .withColumn("timestamp", current_timestamp()) \
        .select("stock_name", "last_price", "time", "timestamp")
    
    print("\nStarting streaming query...")
    print("=" * 80)
    
    # Write to console
    query = processed_df.writeStream \
        .format("console") \
        .outputMode("append") \
        .option("truncate", False) \
        .start()
    
    # Run for 30 seconds
    print("\nStreaming data for 30 seconds...\n")
    time.sleep(30)
    
    print("\n" + "=" * 80)
    print("Stopping query...")
    query.stop()
    
    print("Stopping Spark...")
    spark.stop()
    
    print("\n✅ Example completed successfully!")


if __name__ == "__main__":
    main()

