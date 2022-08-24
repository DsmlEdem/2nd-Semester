import findspark
findspark.init() 
from pyspark.sql import SparkSession
import csv,time
from operator import add

spark = SparkSession.builder.appName("SparkRDD_Q6_RDD").config("spark.ui.port", "4041").getOrCreate()

sc = spark.sparkContext

rdd = sc.textFile("hdfs://master:9000/files/charts.csv")\
        .map(lambda x : list(csv.reader([x], delimiter=',', quotechar='"'))[0])

artists = sc.textFile("hdfs://master:9000/files/artists.csv")\
            .map(lambda x : list(csv.reader([x], delimiter=',', quotechar='"'))[0])

mapping = sc.textFile("hdfs://master:9000/files/chart_artist_mapping.csv")\
            .map(lambda x : list(csv.reader([x], delimiter=',', quotechar='"'))[0])

regions = sc.textFile("hdfs://master:9000/files/regions.csv")\
            .map(lambda x : list(csv.reader([x], delimiter=',', quotechar='"'))[0])


start = time.time()

q6 = rdd.filter(lambda x: x[2] =="1" and x[6] == "SAME_POSITION")\
        .map(lambda x: (x[4], (x[0], x[3][:4], x[5])))\
        .join(regions.filter(lambda x: x[1] == "Greece"))\
        .map(lambda x: (x[1][0],1)).reduceByKey(lambda x,y: x+y)\
        .map(lambda x: (x[0][0], (x[0][1], x[0][2], x[1])))\
        .join(mapping).map(lambda x: (x[1][1], x[1][0])).join(artists)\
        .map(lambda x: ((x[1][0][1], x[1][0][0], x[1][1]), x[1][0][2]))\
        .map(lambda x: ((x[0][0], x[0][1], x[1]), x[0][2]))\
        .groupByKey().mapValues(list)\
        .map(lambda x: ((x[0][0], x[0][1]), (x[0][2], x[1])))\
        .reduceByKey(max).map(lambda x: ((x[0][0], x[0][1], x[1][0]), x[1][1]))\
        .flatMapValues(lambda x: x).map(lambda x: (x[0][0], x[0][1], x[1], x[0][2]))\
        .sortBy(lambda x: (x[0], x[1]))

q6.coalesce(1).saveAsTextFile('hdfs://master:9000/outputs/q6_rdd_result.csv')
end = time.time()
total_time = end-start # total time for the query execution (action) and write


with open('time_outputs.txt', 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    data = ['Query 6', 'RDD API', total_time]
    csv_writer.writerow(data)
