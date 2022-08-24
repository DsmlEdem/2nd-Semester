import findspark
findspark.init()

import time, csv
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("SparkSQL").config("spark.ui.port", "4041").getOrCreate()

'''
Q3 Mean daily count of streams of songs in #1 position per month of each year for the top200 charts
'''

charts = spark.read.format("csv").options(header = 'false', inferSchema = 'true').\
               load("hdfs://master:9000/files/charts.csv")
charts.registerTempTable("charts") # Registers this DataFrame as a temporary table using the given name.
# the lifetime of this temporary table is tied to the SparkSession that was used to create this DataFrame.


query3_total = \
"""
SELECT year, month, SUM(streams) / COUNT(DISTINCT(day)) as mean_daily_streams_1
FROM (
    SELECT INT(SUBSTR(_c3, 0, 4)) as year, INT(SUBSTR(_c3, 6, 2)) as month, INT(SUBSTR(_c3, 9, 2)) as day, _c7 as streams 
    FROM charts
    WHERE _c5="top200" AND _c2=1
        )
GROUP BY year, month
ORDER BY year, month
"""

result = spark.sql(query3_total)

start = time.time()
# execute query
result.coalesce(1).write.mode('overwrite').csv('hdfs://master:9000/outputs/q3_sql_result_parquet.csv')
end = time.time()
total_time = end-start # total time for the query execution (action) and write

with open('time_outputs.txt', 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    data = ['Query 3', 'SQL API (csv)', total_time]
    csv_writer.writerow(data)
