import findspark
findspark.init() 
from pyspark.sql import SparkSession
import csv,time

spark = SparkSession.builder.appName("SparkRDD_Q1_RDD").config("spark.ui.port", "4041").getOrCreate()

sc = spark.sparkContext


rdd = sc.textFile("hdfs://master:9000/files/charts.csv")\
        .map(lambda x : list(csv.reader([x], delimiter=',', quotechar='"'))[0])


from operator import add
start = time.time()

q1 = rdd.filter(lambda x: (x[1] == "Shape of You") and (x[5] == "top200"))\
                       .map(lambda x: ("result", int(x[7])))\
                       .reduceByKey(lambda x,y: x+y)

q1.coalesce(1).saveAsTextFile('hdfs://master:9000/outputs/q1_rdd_result.csv')
end = time.time()
total_time = end-start # total time for the query execution (action) and write

with open('time_outputs.txt', 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    data = ['Query 1', 'RDD API', total_time]
    csv_writer.writerow(data)