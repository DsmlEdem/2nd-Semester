import time
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("queries-rdd") \
    .getOrCreate()

sc = spark.sparkContext

tripdata = sc.textFile("hdfs://master:9000/input/yellow_tripdata_1m.csv")


# this won't fit in memory we'll move filtering inside the map
# tripdata = sc.parallelize(tripdata.take(25000))


def splitter(line):
    l = line.split(",")
    l[3] = float(l[3])
    l[4] = float(l[4])
    l[5] = float(l[5])
    l[6] = float(l[6])
    return l


def time_split(time):
    hour = time.split(" ")[1].split(":")[0]
    return hour


def preprocess(line):
    if ((line[4] != line[6]) or (line[3] != line[5])) and ((40.496103 <= line[4] <= 45.01585) and (
            40.496103 <= line[6] <= 45.01585) and (
            -79.762152 <= line[3] <= - 71.856214) and (-79.762152 <= line[5] <= -71.856214)):
        return True
    return False


s_time = time.time()
res = tripdata. \
    map(lambda x: splitter(x)). \
    filter(lambda x: preprocess(x)). \
    map(lambda x: (time_split(x[1]), (x[4], x[3], 1))). \
    reduceByKey(lambda x, y: (x[0] + y[0], x[1] + y[1], x[2] + y[2])).sortByKey().mapValues(
    lambda x: (x[0] / x[2], x[1] / x[2]))

for i in res.collect():
    print(i)
end_time = time.time()

print("Time taken for RDD query 1 is {} seconds".format(end_time - s_time))

