import findspark
findspark.init() 
from pyspark.sql import SparkSession
import csv,time

spark = SparkSession.builder.appName("SparkRDD_Q2_RDD").config("spark.ui.port", "4041").getOrCreate()

sc = spark.sparkContext


rdd = sc.textFile("hdfs://master:9000/files/charts.csv")\
        .map(lambda x : list(csv.reader([x], delimiter=',', quotechar='"'))[0])


from operator import add
start = time.time()
q2_result = rdd.filter(lambda x: x[1] != "+")\
               .filter(lambda x: x[2] == '1')\
               .map(lambda x: ((x[1], x[5]), 1))\
               .reduceByKey(add)\
               .map(lambda x: ((x[0][1], x[1]), x[0][0]))\
               .sortByKey(ascending=False)\
               .map(lambda x: ((x[0][0]), (x[0][1], x[1])))\
               .reduceByKey(max)\
               .map(lambda x: (x[0], x[1][1], x[1][0]/69))\
	       .map(lambda s: ','.join(str(d) for d in s))
q2_result.coalesce(1).saveAsTextFile('hdfs://master:9000/outputs/q2_rdd_result.csv')
end = time.time()
total_time = end-start # total time for the query execution (action) and write

with open('time_outputs.txt', 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    data = ['Query 2', 'RDD API', total_time]
    csv_writer.writerow(data)

