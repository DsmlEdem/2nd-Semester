from pyspark.sql import SparkSession
from datetime import datetime
import time

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

def date_in_range(row):
    date = datetime.strptime(row[0][2:], "%y-%m-%dT%H:%M:%SZ")
    mindate = datetime.strptime("17-03-22 22:00", "%y-%m-%d %H:%M")
    maxdate = datetime.strptime("17-03-22 23:00", "%y-%m-%d %H:%M")
    return date >= mindate and date <= maxdate

start_time = time.time()

result = sc.textFile("hdfs://master:9000/user/user/files/warc.csv") \
            .map(parse_row) \
            .filter(lambda row: row[0] != "") \
            .filter(date_in_range) \
            .map(lambda row: (row[6], 1)) \
            .reduceByKey(lambda x, y: x + y) \
            .map(lambda t: (t[1], t[0])) \
            .sortByKey(ascending=False)

end_time = time.time()
elapsed = end_time - start_time

print(result.collect())
print(f"Time elapsed: {elapsed} seconds")



