import time
import findspark
findspark.init()
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("csv_to_parquet").config("spark.ui.port","4040").config("spark.executor.memory", "2g").getOrCreate()
sc = spark.sparkContext
#sc.setLogLevel("WARN")

# Adjust the HDFS path 
path = "/"

# Here we load the .csv files as spark DataFrames

# -> inferSchema = true is used in order to have the correct data types
# for example, the first column is read as string instead of int with inferSchema = false

# -> header = false is used because there are no headers
# In fact, we will rename all columns in order to suit our needs
# The names are given based on the documentation by N. Provatas

csv_names = ["artists","charts","regions","chart_artist_mapping"]
filesfolder = "files/"
dfs = []

for name in csv_names:
    dfs.append(spark.read.option("header","false").option("inferSchema","true").csv(path+filesfolder+name+".csv"))

dfs[0] = dfs[0].withColumnRenamed("_c0","ART_ID").withColumnRenamed("_c1","ART_NAME")

dfs[1] = dfs[1].withColumnRenamed("_c0","SONG_ID").withColumnRenamed("_c1","SONG_NAME").withColumnRenamed("_c2","POS").\
                withColumnRenamed("_c3","DATE").withColumnRenamed("_c4","REG_ID").withColumnRenamed("_c5","CHART").\
                withColumnRenamed("_c6","ACTION").withColumnRenamed("_c7","STREAMS")

dfs[2] = dfs[2].withColumnRenamed("_c0","REG_ID").withColumnRenamed("_c1","REG_NAME")

dfs[3] = dfs[3].withColumnRenamed("_c0","SONG_ID").withColumnRenamed("_c1","ART_ID")

# We time the saving time, even though the assignment does not require us to do so
tick = time.time()
for idx,name in enumerate(csv_names):
    dfs[idx].write.parquet(path+filesfolder+name+".parquet")
tack = time.time()

dt = tack-tick
print('The time required to save the Parquet files was ', round(dt, 2),' seconds.')
