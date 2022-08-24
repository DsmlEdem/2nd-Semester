import findspark
findspark.init()

import time, csv
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("SparkSQL").config("spark.ui.port", "4041").getOrCreate()

'''
Q3 Mean daily count of streams of songs in #1 position per month of each year for the top200 charts
'''

# read data
charts = spark.read.format("csv").options(header = 'false', inferSchema = 'true').\
               load("hdfs://master:9000/files/charts.csv")
charts.registerTempTable("charts") # Registers this DataFrame as a temporary table using the given name.
# the lifetime of this temporary table is tied to the SparkSession that was used to create this DataFrame.

regions = spark.read.format("csv").options(header = 'false', inferSchema = 'true').\
               load("hdfs://master:9000/files/regions.csv")
regions.registerTempTable("regions") # Registers this DataFrame as a temporary table using the given name.
# he lifetime of this temporary table is tied to the SparkSession that was used to create this DataFrame.


query4_1 = \
"""
SELECT _c4 as country, _c0 as song_id, _c1 as song_name, COUNT(_c0) as count_in_viral50
FROM charts
WHERE _c5="viral50"
GROUP BY country, song_id, song_name
"""

table3 = spark.sql(query4_1)
table3.registerTempTable("table3")

query4_2 = \
"""
SELECT country, MAX(count_in_viral50) as max_count_in_viral50
FROM table3
GROUP BY country
"""

table4 = spark.sql(query4_2)
table4.registerTempTable("table4")

query4_3 = \
"""
SELECT regions._c1, table3.song_id, table3.song_name, table4.max_count_in_viral50
FROM table4
INNER JOIN table3
ON table4.country=table3.country AND table4.max_count_in_viral50=table3.count_in_viral50
INNER JOIN regions
ON table4.country=regions._c0
ORDER BY regions._c1, song_id
"""

result = spark.sql(query4_3)

start = time.time()
# execute query
result.coalesce(1).write.mode('overwrite').csv('hdfs://master:9000/outputs/q4_sql_result.csv')
end = time.time()
total_time = end-start # total time for the query execution (action) and write

with open('time_outputs.txt', 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    data = ['Query 4', 'SQL API (csv)', total_time]
    csv_writer.writerow(data)
