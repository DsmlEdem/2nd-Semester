from pyspark.sql import SparkSession
import sys
import time
disabled = sys.argv[1]
spark = SparkSession.builder.appName('query1-sql').getOrCreate()
if disabled == "Y":
 spark.conf.set("spark.sql.autoBroadcastJoinThreshold",-1)
elif disabled == 'N':
 pass
else:
 raise Exception ("This setting is not available.")
df = spark.read.format("parquet")
df1 = df.load("hdfs://master:9000/input/yellow_tripdata_1m.parquet")
df2 = df.load("hdfs://master:9000/input/yellow_tripvendors_1m.parquet")
df1.registerTempTable("tripdata")
df2.registerTempTable("tripvendors")
sqlString = \
"SELECT * " + \
"FROM " + \
" (SELECT * FROM tripvendors LIMIT 100) as v, " + \
" tripdata as d " + \
"WHERE " + \
" v.ID = d.ID"
t1 = time.time()
spark.sql(sqlString).collect()
t2 = time.time()
spark.sql(sqlString).explain()
print("Time with choosing join type %s is %.4f sec."%("enabled" if disabled
== 'N' else "disabled", t2-t1))
