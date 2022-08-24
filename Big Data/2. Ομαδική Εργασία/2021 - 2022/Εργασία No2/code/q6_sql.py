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

artists_map = spark.read.format("csv").options(header = 'false', inferSchema = 'true').\
               load("hdfs://master:9000/files/chart_artist_mapping.csv")
artists = spark.read.format("csv").options(header = 'false', inferSchema = 'true').\
               load("hdfs://master:9000/files/artists.csv")

artists_map.registerTempTable("artists_map")
artists.registerTempTable("artists")


query6_1 = \
"""
SELECT charts._c5 as chart, INT(SUBSTR(charts._c3, 0, 4)) as year, charts._c0 as song_id, COUNT(charts._c0) as consecutive_1
FROM regions
INNER JOIN charts
ON regions._c0=charts._c4 AND regions._c1="Greece" AND charts._c6="SAME_POSITION" AND charts._c2=1
GROUP BY chart, year, song_id
"""

table8 = spark.sql(query6_1)
table8.registerTempTable("table8")

query6_2 = \
"""
SELECT chart, year, MAX(consecutive_1) as max_consecutive_1
FROM table8
GROUP BY chart, year
"""

table9 = spark.sql(query6_2)
table9.registerTempTable("table9")

query6_3 = \
"""
SELECT table9.chart, table9.year, artists._c1, table9.max_consecutive_1
FROM table9
INNER JOIN table8
ON table8.chart = table9.chart AND table8.year=table9.year AND table8.consecutive_1=table9.max_consecutive_1
INNER JOIN artists_map
ON artists_map._c0=table8.song_id
INNER JOIN artists
ON artists._c0=artists_map._c1
ORDER BY table9.chart ASC, table9.year DESC
"""


result = spark.sql(query6_3)

start = time.time()
# execute query
result.coalesce(1).write.mode('overwrite').csv('hdfs://master:9000/outputs/q6_sql_result.csv')
end = time.time()
total_time = end-start # total time for the query execution (action) and write

with open('time_outputs.txt', 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    data = ['Query 6', 'SQL API (csv)', total_time]
    csv_writer.writerow(data)
