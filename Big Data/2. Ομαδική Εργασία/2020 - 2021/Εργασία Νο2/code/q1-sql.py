from pyspark.sql import SparkSession
from pyspark.sql.functions import datediff
import sys
import time
spark = SparkSession.builder.appName('ssql').getOrCreate()
sc = spark.sparkContext 
spark.sparkContext.setLogLevel('WARN')
spark.catalog.clearCache()

# execution: spark-submit q1-sql.py 0 for parquet or 1 for csv.
use_csv = int(sys.argv[1])
if use_csv == 1:
    use_csv = True
else: 
    use_csv = False
start = time.time()

if use_csv:
    tripdata = spark.read.load("hdfs://master:9000/project1/yellow_tripdata_1m.csv", format='csv', inferSchema="true")
else:
    tripdata = spark.read.load("hdfs://master:9000/project1/tripdata.parquet")

tripdata.registerTempTable("tripdata")

query1 = \
    """
    SELECT HOUR(_c1) as HOUR,
    AVG(_c3) as LONG,
    AVG(_c4) as LAT
    FROM tripdata 
    WHERE _c1 < _c2 AND _c3 <> _c5 AND
    _c4 <> _c6 AND _c3 <> 0 AND _c4 <> 0 AND 
    _c5 <> 0 AND _c6 <> 0
    GROUP BY HOUR
    ORDER BY HOUR ASC
    """


for line in spark.sql(query1).collect():
    print(line)

end = time.time()
if use_csv:
    print('Elapsed Time using csv: {} seconds!'.format(round(end-start,2)))
else:
    print('Elapsed Time using parquet: {} seconds!'.format(round(end-start,2)))

