import findspark
findspark.init() 
from pyspark.sql import SparkSession
import csv,time
from operator import add

spark = SparkSession.builder.appName("SparkRDD_Q3_RDD").config("spark.ui.port", "4041").getOrCreate()

sc = spark.sparkContext


rdd = sc.textFile("hdfs://master:9000/files/charts.csv")\
        .map(lambda x : list(csv.reader([x], delimiter=',', quotechar='"'))[0])

start = time.time()
q3 = rdd.filter(lambda x : (x[5] == "top200" and (x[2] == "1")))\
        .map(lambda x : ((x[3].split("-")[0], x[3].split("-")[1],
                          x[3].split("-")[2].split("T")[0]),int(x[7])))\
        .reduceByKey(add).map(lambda x: ((x[0][0],x[0][1]), [1,x[1]]))\
        .reduceByKey(lambda x,y: (x[0]+y[0], x[1]+y[1]))\
        .sortByKey().map(lambda x: (int(x[0][0]), int(x[0][1]), x[1][1]/x[1][0]))

q3.coalesce(1).saveAsTextFile('hdfs://master:9000/outputs/q3_rdd_result.csv')
end = time.time()
total_time = end-start # total time for the query execution (action) and write

with open('time_outputs.txt', 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    data = ['Query 3', 'RDD API', total_time]
    csv_writer.writerow(data)

