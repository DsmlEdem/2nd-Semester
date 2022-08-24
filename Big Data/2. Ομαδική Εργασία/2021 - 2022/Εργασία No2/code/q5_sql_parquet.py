import findspark
findspark.init()

import time, csv
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("SparkSQL_Q5_sql").config("spark.ui.port", "4041").getOrCreate()

'''
Q3 Mean daily count of streams of songs in #1 position per month of each year for the top200 charts
'''

# read data
charts = spark.read.parquet("hdfs://master:9000/files/charts.parquet")
charts.registerTempTable("charts") # Registers this DataFrame as a temporary table using the given name.
# the lifetime of this temporary table is tied to the SparkSession that was used to create this DataFrame.

artists_map = spark.read.parquet("hdfs://master:9000/files/chart_artist_mapping.parquet")
artists_map.registerTempTable("artists_map") # Registers this DataFrame as a temporary table using the given name.

artists = spark.read.parquet("hdfs://master:9000/files/artists.parquet")
artists.registerTempTable("artists") # Registers this DataFrame as a temporary table using the given name.


query5_1 = \
"""
SELECT INT(SUBSTR(_c3, 0, 4)) as year, artists._c1 as artist, SUM(charts._c7) as total_streams
FROM charts
INNER JOIN artists_map 
ON charts._c0=artists_map._c0
INNER JOIN artists
ON artists_map._c1=artists._c0
WHERE charts._c5="top200"
GROUP BY year, artist
"""

table5 = spark.sql(query5_1)
table5.registerTempTable("table5")

query5_2 = \
"""
SELECT year, MAX(total_streams) as max_streams
FROM table5
GROUP BY year
"""

table6 = spark.sql(query5_2)
table6.registerTempTable("table6")

query5_3 = \
"""
SELECT table5.year, table5.artist, table6.max_streams/69 as max_mean_streams
FROM table5
INNER JOIN table6
ON table5.year=table6.year AND table5.total_streams=table6.max_streams
ORDER BY year ASC
"""

result = spark.sql(query5_3)

start = time.time()
# execute query
result.coalesce(1).write.mode('overwrite').csv('hdfs://master:9000/outputs/q5_sql_result_parquet.csv')
end = time.time()
total_time = end-start # total time for the query execution (action) and write

with open('time_outputs.txt', 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    data = ['Query 5', 'SQL API (parquet)', total_time]
    csv_writer.writerow(data)
