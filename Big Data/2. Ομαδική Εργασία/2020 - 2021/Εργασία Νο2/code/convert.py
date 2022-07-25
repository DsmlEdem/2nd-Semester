from pyspark.sql import SparkSession
import time

spark = SparkSession.builder.appName("csv2parquet").getOrCreate()
spark.sparkContext.setLogLevel('WARN')
start_read = time.time()
data1 = spark.read.format("csv").options(header='false', inferSchema = 'true').load("hdfs://master:9000/project1/yellow_tripdata_1m.csv")
data2 = spark.read.format("csv").options(header='false', inferSchema = 'true').load("hdfs://master:9000/project1/yellow_tripvendors_1m.csv")
end_read = time.time()

start_write = time.time()
data1.write.parquet('hdfs://master:9000/project1/tripdata.parquet')
data2.write.parquet('hdfs://master:9000/project1/tripvendors.parquet')
end_write = time.time()
print('***********************************************')
print("Time taken to read both .csv files {:.2f} and time taken to write both parquet files {:.2f}".format(end_read-start_read, end_write-start_write))
print('***********************************************') 
