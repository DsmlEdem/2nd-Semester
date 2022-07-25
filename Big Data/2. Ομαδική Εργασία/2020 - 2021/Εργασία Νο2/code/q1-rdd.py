import time
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('q1-rdd').getOrCreate()
sc = spark.sparkContext
spark.sparkContext.setLogLevel('WARN')

def clean(x):
    """
    Simple function that cleans data by checking:
    1. Time consistency
    2. Start - End Coordinates Consistency
    3. Coordinates are non-zero
    """
    if x:
        values = x.split(",")
        time_start = int(values[1].split(" ")[1].split(":")[0])
        time_end = int(values[2].split(" ")[1].split(":")[0])
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
                return (time_start,lat_start,long_start)


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

#Q1-RDD
start = time.time()
res = sc.textFile("hdfs://master:9000/project1/yellow_tripdata_1m.csv")\
    .map(clean)\
    .filter(lambda x: x)\
    .map(lambda x: (x[0], (x[1], x[2], 1)))\
    .reduceByKey(lambda a,b: tuple(i+j for i, j in zip(a, b)))\
    .mapValues(lambda x: (x[0]/x[2], x[1]/x[2]))\
    .sortByKey(ascending=True)\
    .collect()
end = time.time()
print('*********************************************')
print('*********************************************')
for i in res:
    print(i)
print('*********************************************')
print('TIME TAKEN: {}'.format(end-start))
print('*********************************************')


