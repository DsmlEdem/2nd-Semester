import findspark
findspark.init() 
from pyspark.sql import SparkSession
import csv,time
from operator import add

spark = SparkSession.builder.appName("SparkRDD_Q4_RDD").config("spark.ui.port", "4041").getOrCreate()

sc = spark.sparkContext


rdd = sc.textFile("hdfs://master:9000/files/charts.csv")\
        .map(lambda x : list(csv.reader([x], delimiter=',', quotechar='"'))[0])
regions = sc.textFile("hdfs://master:9000/files/regions.csv").\
        map(lambda x : list(csv.reader([x], delimiter=',', quotechar='"'))[0])


start = time.time()
q4 = rdd.filter(lambda x: x[5] == "viral50")\
        .map(lambda x: ((x[4], x[0], x[1]), 1))\
        .reduceByKey(add)\
        .map(lambda x: ((x[0][0],x[1]),[x[0][1], x[0][2]]))\
        .groupByKey().mapValues(list)\
        .map(lambda x: (x[0][0], (x[0][1], x[1])))\
        .reduceByKey(max).map(lambda x: ((x[0], x[1][0]), x[1][1]))\
        .flatMapValues(lambda x: x).map(lambda x: (x[0][0], (x[1], x[0][1])))\
        .join(regions)\
        .map(lambda x : (x[1][1], int(x[1][0][0][0]), x[1][0][0][1], x[1][0][1]))\
        .sortBy(lambda x: x)


q4.coalesce(1).saveAsTextFile('hdfs://master:9000/outputs/q4_rdd_result.csv')
end = time.time()
total_time = end-start # total time for the query execution (action) and write

with open('time_outputs.txt', 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    data = ['Query 4', 'RDD API', total_time]
    csv_writer.writerow(data)
