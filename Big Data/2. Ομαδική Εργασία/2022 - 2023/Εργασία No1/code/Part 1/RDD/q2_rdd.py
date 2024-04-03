from pyspark.sql import SparkSession
from datetime import datetime

sc = SparkSession \
    .builder \
    .appName("Part 1 RDD query 2 execution") \
    .getOrCreate() \
    .sparkContext

def parse_row(row):
    row = row.split(",")
    fields = row[:7]
    final_field = ",".join(row[7:])
    fields.append(final_field)
    return fields

warc = sc.textFile("hdfs://master:9000/user/user/files/warc.csv") \
            .map(parse_row) \
            .filter(lambda row: row[5] == "http://1001.ru/articles/post/ai-da-tumin-443" and row[2] == "request") \
            .map(lambda row: (row[1], row))

wat = sc.textFile("hdfs://master:9000/user/user/files/wat.csv") \
            .map(lambda row: row.split(",")) \
            .map(lambda row: (row[0], (row[1], row[2])))

result = warc.join(wat) \
        .map(lambda t: (len(t[1][0][7]), t[1][1][0]))

print(result.collect())



