from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, FloatType, StringType, TimestampType, ArrayType
from pyspark.sql.functions import col, udf, explode, count, split
from pprint import pprint
import re

spark = SparkSession \
    .builder \
    .appName("SQL on CSV query 5 execution") \
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

warc_df = spark.read.csv("files/warc.csv", header=False, schema=warc_schema, quote='"', escape='"')

targetHTML = warc_df.withColumn("all_urls", explode(split(warc_df["html_dom"], "http[s]?://")))
targetHTML.registerTempTable("warc")

query = """
SELECT all_urls, COUNT(*) AS cnt
FROM warc
GROUP BY all_urls
ORDER BY cnt DESC
LIMIT 10
"""
result = spark.sql(query)
pprint(result.show(10))


# targetHTML = targetHTML.withColumn("html_dom_urls", html_to_urls_udf(col("html_dom")))
# targetHTML.show(5)

# exploded_df = targetHTML.select(explode(col("html_dom_urls")).alias("single_url"))

# urls_with_counts = exploded_df.groupBy("single_url").agg(count("*").alias("count"))
# urls_with_counts.show(10)



