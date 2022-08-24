import findspark
findspark.init()

import time, csv
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("SparkSQL").config("spark.ui.port", "4041").getOrCreate()

'''
Q2 song with max mean time of presence in #1 for each chart 
'''

charts = spark.read.format("csv").options(header = 'false', inferSchema = 'true').\
               load("hdfs://master:9000/files/charts.csv")
charts.registerTempTable("charts") # Registers this DataFrame as a temporary table using the given name.
# the lifetime of this temporary table is tied to the SparkSession that was used to create this DataFrame.

query2_2 = \
"""
SELECT _c5 as chart, _c1 as song, COUNT(*) as times_at_top
        FROM charts
        WHERE _c2=1 
        GROUP BY chart, song
        ORDER BY chart, times_at_top DESC
"""
table1 = spark.sql(query2_2)
table1.registerTempTable("table1") # create table 1

query2_3 = \
"""
SELECT table2.chart, table1.song, table2.max_times_at_top/69 as max_mean_time_at_top
FROM 
    (SELECT chart, MAX(times_at_top) as max_times_at_top
    FROM table1
    GROUP BY chart) as table2
INNER JOIN table1
ON table2.chart=table1.chart AND table2.max_times_at_top=table1.times_at_top
"""

result = spark.sql(query2_3)

start = time.time()
# execute query
result.coalesce(1).write.mode('overwrite').csv('hdfs://master:9000/outputs/q2_sql_result.csv')
end = time.time()
total_time = end-start # total time for the query execution (action) and write

with open('time_outputs.txt', 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    data = ['Query 2', 'SQL API (csv)', total_time]
    csv_writer.writerow(data)
