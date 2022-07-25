import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

import numpy as np
import pandas as pd

maincol = '#486393'
complcol = '#818fa3'
complcol2 = '#a3babf'
sns.set(style = "darkgrid")


# Load the time results
dts_a = pd.read_csv("../outputs/CSV_times.csv", header=None)[1].values
dts_b = pd.read_csv("../outputs/Parquet_times.csv", header=None)[1].values
dts_c = pd.read_csv(path+"outputs/RDD_times.csv", header=None)[1].values

dts_a = np.round_(dts_a, decimals=3)
dts_b = np.round_(dts_b, decimals=3)
dts_c = np.round_(dts_c, decimals=3)

labels = ["RDD API", "Spark SQL (CSV)", "Spark SQL (Parquet)"]

for idx in range(dts_a.shape[0]):

    fig, ax = plt.subplots(1,1)

    inputs = [dts_c[idx],dts_a[idx],dts_b[idx]]
    ylimm = dts_c[idx]*1.1

    ax.bar(labels, inputs, width=0.5, align='center', color=maincol, alpha=0.8)
    ax.bar_label(ax.containers[0])
    ax.set_ylim((0,ylimm))

    plt.ylabel('Execution Time (s)')
    plt.title('Query No. {}'.format(idx+1))

    plt.savefig('../outputs/figures/query{}.pdf'.format(idx+1), bbox_inches='tight')

minidf = {'Query' : ['Query 1', 'Query 1', 'Query 1', 'Query 2', 'Query 2', 'Query 2',
                     'Query 3', 'Query 3', 'Query 3', 'Query 4', 'Query 4', 'Query 4',
                     'Query 5', 'Query 5', 'Query 5', 'Query 6', 'Query 6', 'Query 6'],
          'Item' : [labels[0], labels[1], labels[2], labels[0], labels[1], labels[2],
                    labels[0], labels[1], labels[2], labels[0], labels[1], labels[2], 
                    labels[0], labels[1], labels[2], labels[0], labels[1], labels[2]],
          'Time' : [dts_c[0], dts_a[0], dts_b[0], dts_c[1], dts_a[1], dts_b[1],
                    dts_c[2], dts_a[2], dts_b[2], dts_c[3], dts_a[3], dts_b[3],
                    dts_c[4], dts_a[4], dts_b[4], dts_c[5], dts_a[5], dts_b[5]]}

palette ={labels[0]: maincol, labels[1]: complcol, labels[2]: complcol2}

minidf = pd.DataFrame(minidf)

ylimm = 1.1*dts_c.max()

sns.set(font_scale=1.25)
fig, ax = plt.subplots(1,1, figsize=(11,5))

ax = sns.barplot(x='Query', y='Time', hue='Item', data=minidf, alpha=0.8, palette=palette)

#for container in ax.containers:
#    ax.bar_label(container)
ax.set_ylim((0,ylimm))

plt.ylabel('Execution Time (s)')
plt.xlabel('')
plt.title('Concentrated results for all queries')
plt.legend(loc='upper left')

plt.savefig('../outputs/figures/all_queries.pdf', bbox_inches='tight')

import findspark
findspark.init()
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName('build-joins-graph').config("spark.executor.memory", "2g").getOrCreate()

# Adjust the HDFS path
HDFS_PATH = "/"

# Parse the values for enabled and disabled times
jdf = spark.read.csv(HDFS_PATH+"files/join_experiment.csv").toPandas()
enabled_time = round(float(jdf[jdf['_c0']=='Enabled'].iloc[0,1]),3)
disabled_time = round(float(jdf[jdf['_c0']=='Disabled'].iloc[0,1]),3)

times = [enabled_time, disabled_time]
labels = ["Enabled", "Disabled"]

sns.set(font_scale=1)
fig, ax = plt.subplots(1,1)

ylimm = 1.1*max(times)

ax.bar(labels, times, width=0.25, color=maincol, alpha=0.8)
ax.bar_label(ax.containers[0])
ax.set_ylim((0,ylimm))

plt.ylabel('Execution Time (s)')
plt.title("Options for Spark's Join Optimizer")

plt.savefig('../outputs/figures/joinoptim.pdf', bbox_inches='tight')
