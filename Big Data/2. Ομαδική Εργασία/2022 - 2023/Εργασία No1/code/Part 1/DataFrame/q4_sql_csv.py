from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, FloatType, StringType, TimestampType
from pyspark.sql.functions import col
from datetime import datetime


spark = SparkSession \
    .builder \
    .appName("DF query 2 execution") \
    .getOrCreate() 

warc_schema = StructType([
    StructField("date", TimestampType()),
    StructField("id", StringType()),
    StructField("type", StringType()),
    StructField("content_length", IntegerType()),
    StructField("public_ip", StringType()),
    StructField("target_url", StringType()),
    StructField("server", StringType()),
    StructField("html_dom", StringType()),
])
wat_schema = StructType([
    StructField("warc_record_id", StringType()),
    StructField("metadata_content_length", IntegerType()),
    StructField("targetURL", StringType()),
])

warc_df = spark.read.csv("files/warc.csv", header=False, schema=warc_schema, quote='"', escape='"')
wat_df = spark.read.csv("files/wat.csv", header=False, schema=wat_schema, quote='"', escape='"')

warc_df.registerTempTable("warc")
wat_df.registerTempTable("wat")

query = f"""
SELECT server, AVG(warc.content_length) as avg_cont_len, AVG(wat.metadata_content_length) as avg_meta_cont_len
FROM warc
INNER JOIN wat
ON warc.id = wat.warc_record_id
GROUP BY warc.server
ORDER BY avg_cont_len DESC
LIMIT 5
"""
result = spark.sql(query)
result.show()



