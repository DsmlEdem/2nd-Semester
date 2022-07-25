import time
import math
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import DoubleType

spark = SparkSession.builder \
	.appName("sql_csv") \
	.getOrCreate()

sc = spark.sparkContext

tripdata = spark.read.format("csv").options(header="false",inferSchema="true").load("hdfs://master:9000/input/yellow_tripdata_1m.csv")

tripdata = tripdata.withColumnRenamed("_c0","ID") \
        .withColumnRenamed("_c1","Start") \
        .withColumnRenamed("_c2","End") \
        .withColumnRenamed("_c3","S_Lon") \
        .withColumnRenamed("_c4","S_Lat") \
        .withColumnRenamed("_c5","E_Lon") \
        .withColumnRenamed("_c6","E_Lat") \
        .withColumnRenamed("_c7","Cost")


tripvendors = spark.read.format("csv").options(header="false",inferSchema="true").load("hdfs://master:9000/input/yellow_tripvendors_1m.csv")

tripvendors = tripvendors.withColumnRenamed("_c0","ID") \
        .withColumnRenamed("_c1","Vendor")


# define a table (registerTempTable)
tripdata.registerTempTable("TRIPDATA")
# First Query
sqlString = "SELECT hour(Start) as HourOfDay, AVG(S_Lat) as Latitude, AVG(S_Lon) as Longitude FROM TRIPDATA " + \
"WHERE (S_Lon >= -79.762152 AND S_Lon <= -71.856214 AND S_Lat >= 40.496103 AND S_Lat <= 45.01585 " + \
"AND E_Lon >= -79.762152 AND E_Lon <= -71.856214 AND E_Lat >= 40.496103 AND E_Lat <= 45.01585) " + \
"AND (S_Lat != E_Lat OR S_Lon != E_Lon) " + \
"GROUP BY HourOfDay " + \
"ORDER BY HourOfDay ASC"

q1_start = time.time()
res = spark.sql(sqlString)
res.show(24)
q1_end = time.time()
print("Time taken for first query is {} seconds".format(q1_end-q1_start))

# Second Query

def haversine_dist(phi1,phi2,l1,l2):
    R = 6371
    phi1 = phi1*math.pi/180
    phi2 = phi2*math.pi/180
    dl = (l2-l1)*math.pi/180
    a= math.sin((phi2-phi1)/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dl/2)**2
    c = 2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    d = R*c
    return d


haversine = udf(haversine_dist, DoubleType())
tripdata = tripdata.withColumn("Distance", haversine("S_Lat", "E_Lat", "S_Lon", "E_Lon"))

joined = tripdata.join(tripvendors,'ID')
joined.registerTempTable("JOINED")

q2_start=time.time()
spark.sql("SELECT Vendor, distance, Time FROM " + \
"(SELECT Vendor, (unix_timestamp(End) - unix_timestamp(Start))/3600 as Time, distance, " + \
"RANK() OVER (PARTITION BY Vendor ORDER BY distance DESC) as Rank FROM JOINED " + \
"WHERE (S_Lon >= -79.762152 AND S_Lon <= -71.856214 AND S_Lat >= 40.496103 AND S_Lat <= 45.01585 " + \
"AND E_Lon >= -79.762152 AND E_Lon <= -71.856214 AND E_Lat >= 40.496103 AND E_Lat <= 45.01585) " + \
"AND (S_Lat != E_Lat OR S_Lon != E_Lon) " + \
"AND distance / ((unix_timestamp(End) - unix_timestamp(Start))/3600) < 200) WHERE Rank=1").show()

q2_end = time.time()
print("Time taken for second query is {} seconds".format(q2_end-q2_start))

