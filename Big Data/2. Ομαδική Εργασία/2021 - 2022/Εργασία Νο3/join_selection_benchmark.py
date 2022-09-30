from pyspark.sql import SparkSession
import sys, time

spark = SparkSession.builder.appName('study-joins').getOrCreate()


HDFS_PATH = 'files'


'''
    This functions executed a query performing a join. 
    Fill the necessary parts of the function to tune the optimizer 
    regarding the join selection. 

    @arguments:
        - disabled: If the "disabled" argument is set to 
                False, the optimizer should not perform join selection. 

    @returns: 
        The execution time of performing the benchmark join and writing the result
        back to HDFS in parquet format

    @TO-DOs:
        1. Fill in spark.conf.set the appropriate spark optimizer property and 
           property value to disable the optimizer, if user asks so.
        2. Set HDFS_PATH to the hdfs folder containing the charts and regions 
           parquet files
'''

def join_experiment(disabled = False):
    if disabled:
        spark.conf.set('spark.sql.autoBroadcastJoinThreshold', -1)

    df = spark.read.format("parquet")

    df1 = df.load(HDFS_PATH + "/charts.parquet")
    df2 = df.load(HDFS_PATH + "/regions.parquet")

    df1.registerTempTable("charts")
    df2.registerTempTable("regions")

    sqlString = 'select c.*, r.countryName as region_name from charts as c, regions as r where c.countryId = r.countryId'

    t1 = time.time()
    spark.sql(sqlString).write.mode('overwrite').parquet(HDFS_PATH + "/joined_with_optimizer_join_selection_" + str(not disabled) + ".parquet")
    t2 = time.time()

    print("*****************   PHYSICAL PLAN OF JOIN EXPERIMENT WITH OPTIMIZER JOIN SELECTION (DISABLED = " + str(disabled) + ")")
    spark.sql(sqlString).explain()

    return t2 - t1


enabled_time = join_experiment()
disabled_time = join_experiment(disabled = True)
times = [('Enabled', enabled_time), ('Disabled', disabled_time)]

spark.createDataFrame(data=times, schema = ['Optimizer Join Selection', 'Execution Time']).write.mode('overwrite').option('header', 'true').csv(HDFS_PATH + "/join_experiment.csv")
