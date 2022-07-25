from pyspark.sql import SparkSession
import time

spark = SparkSession.builder.appName("parquet_transform").getOrCreate()

sc = spark.sparkContext
sc.setLogLevel("WARN")

tripdata = spark.read.option("header","false").option("inferSchema","true"). \
	csv("hdfs://master:9000/input/yellow_tripdata_1m.csv")

tripvendors = spark.read.option("header","false").option("inferSchema","true"). \
	csv("hdfs://master:9000/input/yellow_tripvendors_1m.csv")

# Change column names for future references
tripdata = tripdata.withColumnRenamed("_c0","ID") \
	.withColumnRenamed("_c1","Start") \
	.withColumnRenamed("_c2","End") \
	.withColumnRenamed("_c3","S_Lon") \
	.withColumnRenamed("_c4","S_Lat") \
	.withColumnRenamed("_c5","E_Lon") \
	.withColumnRenamed("_c6","E_Lat") \
	.withColumnRenamed("_c7","Cost")
tripdata.printSchema()

tripvendors = tripvendors.withColumnRenamed("_c0","ID") \
	.withColumnRenamed("_c1","Vendor")

# Time parquet convertion
start_time = time.time()
tripdata.write.parquet("hdfs://master:9000/input/yellow_tripdata_1m.parquet")
tripvendors.write.parquet("hdfs://master:9000/input/yellow_tripvendors_1m.parquet")
end_time = time.time()

print("Time needed for conversion is {} seconds.".format(end_time-start_time))
