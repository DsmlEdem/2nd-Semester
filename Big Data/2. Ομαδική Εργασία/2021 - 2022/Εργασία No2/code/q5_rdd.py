import findspark
findspark.init() 
from pyspark.sql import SparkSession
import csv,time
from operator import add

spark = SparkSession.builder.appName("SparkRDD_Q5_RDD").config("spark.ui.port", "4041").getOrCreate()

sc = spark.sparkContext

start = time.time()

artists = sc.textFile("hdfs://master:9000/files/artists.csv")\
            .map(lambda x : list(csv.reader([x], delimiter=',', quotechar='"'))[0])

mapping = sc.textFile("hdfs://master:9000/files/chart_artist_mapping.csv")\
            .map(lambda x : list(csv.reader([x], delimiter=',', quotechar='"'))[0])

rdd = sc.textFile("hdfs://master:9000/files/charts.csv")\
        .map(lambda x : list(csv.reader([x], delimiter=',', quotechar='"'))[0])

q5 = rdd.filter(lambda x: (x[5] == "top200") and (x[7]!=""))\
        .map(lambda x: ((x[0], x[3][:4]), int(x[7])))\
        .reduceByKey(add).map(lambda x: (x[0][0], (x[1], x[0][1])))\
        .join(mapping).map(lambda x: ((x[1][1], x[1][0][1]), x[1][0][0]))\
        .reduceByKey(add).map(lambda x: (x[0], x[1]/69))\
        .map(lambda x: (x[0][1], (x[1], x[0][0])))\
        .reduceByKey(max).map(lambda x: (x[1][1], (x[0], x[1][0])))\
        .join(artists).map(lambda x: (x[1][0][0], (x[1][1], x[1][0][1])))\
        .sortByKey().map(lambda x: (x[0], x[1][0], x[1][1]))

q5.coalesce(1).saveAsTextFile('hdfs://master:9000/outputs/q5_rdd_result.csv')
end = time.time()
total_time = end-start # total time for the query execution (action) and write

with open('time_outputs.txt', 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    data = ['Query 5', 'RDD API', total_time]
    csv_writer.writerow(data)
