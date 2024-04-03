from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, FloatType, StringType, TimestampType
from pyspark.sql.functions import col, to_timestamp
from datetime import datetime


spark = SparkSession \
    .builder \
    .appName("DF query 1 execution") \
    .getOrCreate() 

warc_schema = StructType([
    StructField("date", StringType()),
    StructField("id", StringType()),
    StructField("type", StringType()),
    StructField("content_length", IntegerType()),
    StructField("public_ip", StringType()),
    StructField("target_url", StringType()),
    StructField("server", StringType()),
    StructField("html_dom", StringType()),
])

warc_df = spark.read.parquet("files/warc.parquet")
warc_df = warc_df.withColumn("content_length", warc_df["content_length"].cast(IntegerType()))

warc_df = warc_df.withColumn("date", to_timestamp(warc_df["date"], "yyyy-MM-dd'T'HH:mm:ss'Z'"))

warc_df.registerTempTable("warc")

start = datetime(2017, 3, 22, 22, 0, 0)
end = datetime(2017, 3, 22, 23, 0, 0)

query = f"""
SELECT server, COUNT(server) as count
FROM warc
WHERE server IS NOT NULL AND date BETWEEN '{start}' AND '{end}'
GROUP BY server
ORDER BY count DESC;
"""
result = spark.sql(query)
result.show()

# query = """
# SELECT date, id, type, content_length, public_ip, target_url, server
# FROM warc
# LIMIT 10
# """
# result = spark.sql(query)
# result.show()



