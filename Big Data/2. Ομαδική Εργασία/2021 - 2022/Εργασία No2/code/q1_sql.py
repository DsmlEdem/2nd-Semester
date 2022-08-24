import findspark
findspark.init() 

import time, csv
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("SparkSQL").getOrCreate()

'''
Q1 max number of streams for "Shape of You" song on top200 chart
'''

charts = spark.read.format("csv").options(header = 'false', inferSchema = 'true').\
               load("hdfs://master:9000/files/charts.csv")
charts.registerTempTable("charts") # Registers this DataFrame as a temporary table using the given name.
# the lifetime of this temporary table is tied to the SparkSession that was used to create this DataFrame.

query1 = \
    """
        SELECT sum(_c7) as total_streams
        FROM charts
        WHERE _c1="Shape of You" AND _c5="top200"
    """

result = spark.sql(query1)

start = time.time()
# execute query
result.coalesce(1).write.mode('overwrite').csv('hdfs://master:9000/outputs/q1_sql_result.csv')
end = time.time()
total_time = end-start # total time for the query execution (action) and write

with open('time_outputs.txt', 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    data = ['Query 1', 'SQL API (csv)', total_time]
    csv_writer.writerow(data)
