import time
import math
import datetime
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("queries-rdd") \
    .getOrCreate()

sc = spark.sparkContext

tripdata = sc.textFile("hdfs://master:9000/input/yellow_tripdata_1m.csv")
# tripdata = sc.parallelize(tripdata.take(10))

tripvendors = sc.textFile("hdfs://master:9000/input/yellow_tripvendors_1m.csv")
# tripvendros = sc.parallelize(tripvendors.take(10))


def haversine_dist(phi1, phi2, l1, l2):
    R = 6371
    phi1 = phi1 * math.pi / 180
    phi2 = phi2 * math.pi / 180
    dl = (l2 - l1) * math.pi / 180
    a = math.sin((phi2 - phi1) / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dl / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    return d


def max_dist(t1, t2):
    if t1[0] < t2[0]:
        return t2
    return t1


def splitter(line):
    l = line.split(",")
    l[3] = float(l[3])
    l[4] = float(l[4])
    l[5] = float(l[5])
    l[6] = float(l[6])
    return l


def preprocess(line):
    if ((line[4] != line[6]) or (line[3] != line[5])) and ((40.496103 <= line[4] <= 45.01585) and (
            40.496103 <= line[6] <= 45.01585) and (-79.762152 <= line[3] <= - 71.856214) and (
                                                                   -79.762152 <= line[5] <= -71.856214)):
        return True
    return False


def speed_filter(tup):
    _, val = tup
    time, distance = val
    time = time / datetime.timedelta(hours=1)
    if time == 0 or distance / time >= 200:
        return False
    return True

s_time = time.time()
res = tripdata. \
    map(lambda x: splitter(x)). \
    filter(lambda x: preprocess(x)). \
    map(lambda x: (x[0], (
    datetime.datetime.strptime(x[2], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S'),
    haversine_dist(x[4], x[6], x[3], x[5])))). \
    filter(lambda x: speed_filter(x))

tripvendors = tripvendors.map(lambda x: (x.split(",")[0], x.split(",")[1]))

joined = res.join(tripvendors).map(lambda x: (x[1][1], (x[1][0][1], x[1][0][0]/datetime.timedelta(hours=1)))). \
    reduceByKey(max_dist)
for i in joined.collect():
    print(i)
e_time = time.time()
print("Time taken for RDD q2 is {} seconds".format(e_time-s_time))

