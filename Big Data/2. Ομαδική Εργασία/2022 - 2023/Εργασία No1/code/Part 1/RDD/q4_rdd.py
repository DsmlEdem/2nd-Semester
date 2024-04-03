from pyspark.sql import SparkSession
from datetime import datetime

sc = SparkSession \
    .builder \
    .appName("Part 1 RDD query 1 execution") \
    .getOrCreate() \
    .sparkContext

def parse_row(row):
    row = row.split(",")
    fields = row[:7]
    final_field = ",".join(row[7:])
    # fields.append(final_field)
    return fields

def drop_null(row):
    if any(not element for element in row):
        return False
    return True

warc = sc.textFile("hdfs://master:9000/user/user/files/warc.csv") \
            .map(parse_row) \
            .filter(drop_null) \
            .map(lambda row: (row[1], row))

wat = sc.textFile("hdfs://master:9000/user/user/files/wat.csv") \
            .map(lambda row: row.split(",")) \
            .map(lambda row: (row[0], row))

def avg(l):
    return sum(l) / len(l)

result = warc.join(wat) \
        .map(lambda t: (t[1][0][6], int(t[1][0][3]), int(t[1][1][1]))) \
        .groupBy(lambda t: t[0]) \
        .map(lambda t: (t[0], avg([y for x, y, z in t[1]]), avg([z for x, y, z in t[1]]))) \
        .sortBy(lambda t: t[1], ascending=False)

print(result.take(5))


