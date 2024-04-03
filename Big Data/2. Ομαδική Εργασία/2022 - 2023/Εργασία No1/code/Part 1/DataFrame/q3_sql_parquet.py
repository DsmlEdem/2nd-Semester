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

warc_df = spark.read.parquet("files/warc.parquet")
warc_df = warc_df.withColumn("date", warc_df["date"].cast(TimestampType()))
warc_df = warc_df.withColumn("content_length", warc_df["content_length"].cast(IntegerType()))

warc_df.registerTempTable("warc")

query = f"""
SELECT warc_ID, targetURL, content_length
FROM warc
WHERE server = "Apache"
ORDER BY content_length DESC
LIMIT 5
"""
result = spark.sql(query)
result.show()



