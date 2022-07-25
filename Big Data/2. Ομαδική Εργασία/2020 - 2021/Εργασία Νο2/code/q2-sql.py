from pyspark.sql import SparkSession
from pyspark.sql.functions import datediff
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType
from datetime import datetime
import sys 
import time
import math

spark = SparkSession.builder.appName('ssql').getOrCreate()
sc = spark.sparkContext 
spark.sparkContext.setLogLevel('WARN')

# execution: spark-submit q1-sql.py 0 for parquet or 1 for csv.
use_csv = int(sys.argv[1])
if use_csv == 1:
    use_csv = True
else: 
    use_csv = False
start = time.time()

def haversine(long1,lat1,long2,lat2):
    long1, lat1, long2, lat2 = map(math.radians, [long1, lat1, long2, lat2])
    # haversine formula 
    dlon = long2 - long1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers
    return c * r

if use_csv:
    tripdata = spark.read.load("hdfs://master:9000/project1/yellow_tripdata_1m.csv", format='csv', inferSchema="true")
    tripvendors = spark.read.load("hdfs://master:9000/project1/yellow_tripvendors_1m.csv", format='csv', inferSchema="true")
else:
    tripdata = spark.read.load("hdfs://master:9000/project1/tripdata.parquet")
    tripvendors = spark.read.load("hdfs://master:9000/project1/tripvendors.parquet")


tripdata = tripdata.toDF("id", "departure", "arrival", "dep_lon", "dep_lat", "arr_lon", "arr_lat", "cost")
tripvendors = tripvendors.toDF("id", "vendors")


haversine_dist = F.udf(haversine, DoubleType())
tripdata = tripdata.withColumn("HavDist", haversine_dist(tripdata.dep_lon,tripdata.dep_lat,tripdata.arr_lon,tripdata.arr_lat))
# tripdata = tripdata.withColumn("HavDist", haversine(tripdata.dep_lon, tripdata.dep_lat, tripdata.arr_lon, tripdata.arr_lat))

# tripdata = tripdata.withColumn('departure',F.to_timestamp(F.col('departure')))\
#   .withColumn('arrival', F.current_timestamp())\
#   .withColumn('time_diff',F.col("arrival").cast("long") - F.col('departure').cast("long"))

tripdata.registerTempTable("tripdata")
tripvendors.registerTempTable("tripvendors")


query2 = """
SELECT tripvendors.vendors, tripdata.HavDist, (UNIX_TIMESTAMP(tripdata.arrival)-UNIX_TIMESTAMP(tripdata.departure)) as time_diff
FROM (tripdata JOIN tripvendors ON tripdata.id = tripvendors.id)
JOIN 
(SELECT tripvendors.vendors as vendor, MAX(tripdata.HavDist) as dist from tripdata 
JOIN tripvendors ON tripdata.id = tripvendors.id 
WHERE (tripdata.departure < tripdata.arrival) AND 
(tripdata.dep_lon <> tripdata.arr_lon) AND
(tripdata.dep_lat <> tripdata.arr_lat) AND
(tripdata.dep_lat <> 0) AND (tripdata.dep_lon <> 0) AND
(tripdata.arr_lat <> 0) AND (tripdata.arr_lon <> 0)
GROUP BY vendor) as sub 
ON tripvendors.vendors = sub.vendor 
AND tripdata.HavDist = sub.dist
ORDER BY tripvendors.vendors ASC 
"""


spark.sql(query2).show()
end = time.time()
if use_csv:
    print('Elapsed Time using csv: {} seconds!'.format(round(end-start,2)))
else:
    print('Elapsed Time using parquet: {} seconds!'.format(round(end-start,2)))

