import findspark
findspark.init()
from pyspark.sql import SparkSession
import sys, time

spark = SparkSession.builder.appName('study-joins').config("spark.executor.memory", "2g").getOrCreate()

# adjust the HDFS path
HDFS_PATH = "/"

'''
    This function executes a query performing a join.

    @arguments:
        - disabled: If the "disabled" argument is set to 
                False, the optimizer should not perform join selection. 

    @returns: 
        The execution time of performing the benchmark join and writing the result
        back to HDFS in parquet format
'''

def join_experiment(disabled = False):
    if disabled:
        spark.conf.set("spark.sql.autoBroadcastJoinThreshold",-1)

    df = spark.read.format("parquet")

    df1 = df.load(HDFS_PATH + "files/charts.parquet")
    df2 = df.load(HDFS_PATH + "files/regions.parquet")

    # registerTempTable was replaced by createOrReplaceTempView, because it is deprecated
    df1.createOrReplaceTempView("charts")
    df2.createOrReplaceTempView("regions")

    # This line was re-written, because the column names were changed for the purposes of our investigation
    #sqlString = 'select c.*, r._c1 as region_name from charts as c, regions as r where c._c4 = r._c0'
    sqlString = 'select c.*, r.REG_NAME as region_name from charts as c, regions as r where c.REG_ID = r.REG_ID'

    t1 = time.time()
    spark.sql(sqlString).write.mode('overwrite').parquet(HDFS_PATH + "files/joined_with_optimizer_join_selection_" + str(not disabled) + ".parquet")
    t2 = time.time()

    print("*****************   PHYSICAL PLAN OF JOIN EXPERIMENT WITH OPTIMIZER JOIN SELECTION (DISABLED = " + str(disabled) + ")")
    spark.sql(sqlString).explain()

    return t2 - t1

enabled_time = join_experiment()
disabled_time = join_experiment(disabled = True)
times = [('Enabled', enabled_time), ('Disabled', disabled_time)]

spark.createDataFrame(data=times, schema = ['Optimizer Join Selection', 'Execution Time']).write.mode('overwrite').option('header', 'true').csv(HDFS_PATH + "files/join_experiment.csv")
