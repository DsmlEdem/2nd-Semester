from pyspark.sql import SparkSession
from datetime import datetime

sc = SparkSession \
    .builder \
    .appName("Part 1 RDD query 3 execution") \
    .getOrCreate() \
    .sparkContext

def parse_row(row):
    row = row.split(",")
    fields = row[:7]
    final_field = ",".join(row[7:])
    # fields.append(final_field)
    return fields

result = sc.textFile("hdfs://master:9000/user/user/files/warc.csv") \
            .map(parse_row) \
            .filter(lambda row: row[6] == "Apache") \
            .map(lambda row: (int(row[3]), (row[1], row[5]))) \
            .sortByKey(ascending=True)

print(result.takeOrdered(5, key=lambda x: -x[0]))



