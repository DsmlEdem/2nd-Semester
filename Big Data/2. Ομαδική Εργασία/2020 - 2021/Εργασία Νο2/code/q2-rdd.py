import time
from pyspark.sql import SparkSession
from math import sin,cos,asin,sqrt,radians
from datetime import datetime


spark = SparkSession.builder.appName('q2-rdd').getOrCreate()
sc = spark.sparkContext
spark.sparkContext.setLogLevel('WARN')

"""
Each Row has the following information:

0 <- trip id
1 <- pickup timestamp
2 <- dropoff timestamp
3 <- pickup longitude
4 <- pickup latitude
5 <- dropoff longitude
6 <- dropoff latitude
7 <- total trip cost
"""

def clean(x):
    """
    Simple function that cleans data by checking:
    1. Time consistency
    2. Start - End Coordinates Consistency
    3. Coordinates are non-zero
    """
    if x:
        values = x.split(",")
        id = int(values[0])
        time_start = str(values[1])
        time_end = str(values[2])
        long_start = float(values[3])
        lat_start = float(values[4])
        long_end = float(values[5])
        lat_end = float(values[6])
        if ((time_start < time_end and 
            long_start != long_end and 
            lat_start != lat_end and 
            lat_start != 0. and
            lat_end != 0. and
            long_start != 0. and
            long_end != 0.)):
                return (id,time_start,time_end,long_start,lat_start,long_end,lat_end)

def haversine(long1,lat1,long2,lat2):
    R = 6371
    long1, lat1, long2, lat2 = map(radians, [long1,lat1,long2,lat2])
    deltaphi = long2-long1
    deltalambda = lat2-lat1
    a = sin(deltaphi/2)**2 + cos(long1)*cos(long2)*sin(0.5*deltalambda)**2
    c = 2*asin(sqrt(a))
    return R*c

start = time.time()
vendors = sc.textFile("hdfs://master:9000/project1/yellow_tripvendors_1m.csv")\
    .map(lambda x: (int(x.split(",")[0]), (int(x.split(",")[1]))))
trips = sc.textFile("hdfs://master:9000/project1/yellow_tripdata_1m.csv")\
        .map(clean)\
        .filter(lambda x: x)\
        .map(lambda x: \
            ( \
            x[0], \
            (haversine(x[3],x[4],x[5],x[6])  ,\
            (datetime.strptime(x[2],'%Y-%m-%d %H:%M:%S')-datetime.strptime(x[1],'%Y-%m-%d %H:%M:%S')).seconds\
            )) \
            )

total = trips.join(vendors).\
    map(lambda x: (x[1][1], x[1][0])).\
    reduceByKey(max).collect()

print(" Vendor","Haversine","Duration(sec)")
for i in total:
    print("  ",i[0],"  ",round(i[1][0],2),"  ", i[1][1])

end = time.time()

print('Elapsed Time: {} seconds!'.format(round(end-start,2)))
