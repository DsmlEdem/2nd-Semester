import findspark
findspark.init() 

from pyspark.sql import SparkSession
import csv
from time import time 
from operator import add
spark = SparkSession.builder.appName("SparkRDD_API").config("spark.ui.port", "4041").config("spark.executor.memory", "2g").getOrCreate()

sc = spark.sparkContext

# Load data

rdd = sc.textFile("/files/charts.csv").map(lambda x : list(csv.reader([x], delimiter=',', quotechar='"'))[0])

countries = sc.textFile("/files/regions.csv").map(lambda x : list(csv.reader([x], delimiter=',', quotechar='"'))[0])

mapping = sc.textFile("/files/chart_artist_mapping.csv").map(lambda x : list(csv.reader([x], delimiter=',', quotechar='"'))[0])

artists = sc.textFile("/files/artists.csv").map(lambda x : list(csv.reader([x], delimiter=',', quotechar='"'))[0])


# Create the logging files

# Start with a blank .txt every time the script is run
with open("../outputs/RDD_Queries.txt", 'w', encoding="utf-8") as f :
	f.write('')
with open("../outputs/RDD_times.csv", 'w', encoding="utf-8") as ft :
	ft.write('')
    
# a list to track the execution times
# WARNING! Track the execution time only the first time of collection
dts = []


# Query 1

tic = time()
# Filter title and chart. Select and keep only the streams number, and aggregate them
Query_1 = rdd.filter(lambda x : (x[1]=="Shape of You") and (x[5]=="top200")).map( lambda x: int(x[7])).reduce(lambda a,b: a+b)
tac = time()
dts.append(tac - tic)
print("Query_1 : Number of streams = ",Query_1)

with open("../outputs/RDD_Queries.txt",'a', encoding="utf-8") as output_f:
    output_f.write(55*"-"+"\nQuery 1 - RDD Version \n"+55*"-"+"\n")
    output_f.write(str(Query_1)+"\n\n")

with open("../outputs/RDD_times.csv",'a') as times_f:
    times_f.write("Query 1, {}  \n".format(dts[0]))


# Query 2

tic = time()
## TOP200 chart

# 1. Filter only entries in the 1st place of the top200 chart and keep only song_name and chart_type.
# 2. count the number of times each song appears, despite country
tmp = rdd.filter(lambda x: (x[2]=='1') and (x[5]=="top200")).map(lambda x: [x[1], x[5]]).countByKey().items()
# Sort by descending order and keep the most popular.
tmp = sorted(tmp, key=lambda item: item[1], reverse=True)[0]
# Divide by the number of countries (69) to get the average for every song. 
Query_2_a = ("top200", tmp[0], tmp[1]/69)

## VIRAL50 chart
tmp = rdd.filter(lambda x: (x[2]=='1') and (x[5]=="viral50")).map(lambda x: [x[1], x[5]]).countByKey().items()
tmp = sorted(tmp, key=lambda item: item[1], reverse=True)[0]
Query_2_b = ("viral50", tmp[0], tmp[1]/69)

tac = time()
dts.append(tac-tic)
print("Query_2_a : ", Query_2_a)
print("Query_2_b : ", Query_2_b)

with open("../outputs/RDD_Queries.txt",'a', encoding="utf-8") as output_f:
    output_f.write(55*"-"+"\nQuery 2 - RDD Version \n"+55*"-"+"\n")
    output_f.write(str(Query_2_a)+"\n\n")
    output_f.write(str(Query_2_b)+"\n\n")

with open("../outputs/RDD_times.csv",'a') as times_f:
    times_f.write("Query 2, {}  \n".format(dts[1]))


# Query 3

tic = time()
# 1. filter entries that have been in the first place of the top200 chart
# 2. Create keys based on year, month, day and aggregate the number of streams in each year-month 
# 3. Substitute the day's number with the number '1'
# 4. Aggregate these numbers '1', to find the number of days in eacb year-month
# 5. Divide aggregated streams with number of days to get the average value
# 6. Sort year-month
Query_3 = rdd.filter(lambda x: (x[5]=="top200") and (x[2]=='1')).map(lambda x: ((int((x[3].split('T')[0][:4])), int(x[3].split('T')[0][5:7]), int(x[3].split('T')[0][8:])),int(x[7]))).reduceByKey(lambda x,y: x+y).map(lambda x: ((x[0][0], x[0][1]), (1, x[1]))).reduceByKey(lambda x,y: (x[0]+y[0], x[1] +y[1])).map(lambda x: (x[0][0], x[0][1], x[1][1]/x[1][0])).sortBy(lambda x : (x[0], x[1]))

Query_3_result = Query_3.take(100)

tac = time()
dts.append(tac-tic)


with open("../outputs/RDD_Queries.txt",'a', encoding="utf-8") as output_f:
    output_f.write(55*"-"+"\nQuery 3 - RDD Version \n"+55*"-"+"\n")
    for row in list(Query_3_result):
        itm = row
        output_f.write("{} {} {} \n".format(itm[0], itm[1], itm[2]))


with open("../outputs/RDD_times.csv",'a') as times_f:
    times_f.write("Query 3, {}  \n".format(dts[2]))


# Query 4

tic = time()
# 1. filter on chart viral50
# 2. format the keys as country_id, song_id, song_name and use digit '1' as value.
#     Then aggregate digits'1' (number of times a song was in viral50 for particular countries)
# 3. Then we group by country
# 4. Technicalities : Make iterator list 
# 5. Use country_id as key 
# 6. Reduce operation to find maximum values. Maximum frequency on viral50
# 7. flatMapValues to split values with the same frequency
# 8. Join with countries csv to get the name of each country by its country id. 
# 9. Format according to the template answer  and sort by country
Query_4 = rdd.filter(lambda x: x[5] == "viral50").map(lambda x: ((x[4], x[0], x[1]), 1)).reduceByKey(add).map(lambda x: ((x[0][0],x[1]),[x[0][1], x[0][2]])).groupByKey().mapValues(list).map(lambda x: (x[0][0], (x[0][1], x[1]))).reduceByKey(max).map(lambda x: ((x[0], x[1][0]), x[1][1])).flatMapValues(lambda x: x).map(lambda x: (x[0][0], (x[1], x[0][1]))).join(countries).map(lambda x : (x[1][1], int(x[1][0][0][0]), x[1][0][0][1], x[1][0][1])).sortBy(lambda x: x)
Query_4_result  = Query_4.take(71)

tac = time()
dts.append(tac - tic)

with open("../outputs/RDD_Queries.txt",'a', encoding="utf-8") as output_f:
    output_f.write(55*"-"+"\nQuery 4 - RDD Version \n"+55*"-"+"\n")
    for row in list(Query_4_result):
        itm = row
        output_f.write("{} {} {} {} \n".format(itm[0], itm[1], itm[2], itm[3]))

with open("../outputs/RDD_times.csv",'a') as times_f:
    times_f.write("Query 4, {}  \n".format(dts[3]))


# Query 5

tic = time()
Query_5 = rdd.filter(lambda x: (x[5] == "top200") and (x[7]!="")).map(lambda x: ((x[0], x[3][:4]), int(x[7]))).reduceByKey(add).map(lambda x: (x[0][0], (x[1], x[0][1]))).join(mapping).map(lambda x: ((x[1][1], x[1][0][1]), x[1][0][0])).reduceByKey(add).map(lambda x: (x[0], x[1]/69)).map(lambda x: (x[0][1], (x[1], x[0][0]))).reduceByKey(max).map(lambda x: (x[1][1], (x[0], x[1][0]))).join(artists).map(lambda x: (x[1][0][0], (x[1][1], x[1][0][1]))).sortByKey().map(lambda x: (x[0], x[1][0], x[1][1]))

Query_5_result = Query_5.take(5)

tac = time()
dts.append(tac - tic)

with open("../outputs/RDD_Queries.txt",'a', encoding="utf-8") as output_f:
    output_f.write(55*"-"+"\nQuery 5 - RDD Version \n"+55*"-"+"\n")
    for row in list(Query_5_result):
        itm = row
        output_f.write("{} {} {} \n".format(itm[0], itm[1], itm[2]))    
        
with open("../outputs/RDD_times.csv",'a') as times_f:
    times_f.write("Query 5, {}  \n".format(dts[4]))


# Query 6

tic = time()
# 1.Filter only entries that have stayed in the first position without moving
# 2. adjust the format and join with countries csv on country_id, filtered for country 'Greece' 
# 3. Employ the digit '1' trick to count the frequency of each song_id in the first position of each chart
# 4. Use song_id as key and join with the mapping csv and then with artists 
# 5. Adjust the format and  groupby chart and year. Frequency is a key and Artists in a list are the values.
# 6. Make frequency the key and the find the maximum frequency for each chart and year
# 7. Split draws to different elements  and then sort by chart and year
Query_6 = rdd.filter(lambda x: x[2] =="1" and x[6] == "SAME_POSITION").map(lambda x: (x[4], (x[0], x[3][:4], x[5]))).join(countries.filter(lambda x: x[1] == "Greece")).map(lambda x: (x[1][0],1)).reduceByKey(lambda x,y: x+y).map(lambda x: (x[0][0], (x[0][1], x[0][2], x[1]))).join(mapping).map(lambda x: (x[1][1], x[1][0])).join(artists).map(lambda x: ((x[1][0][1], x[1][0][0], x[1][1]), x[1][0][2])).map(lambda x: ((x[0][0], x[0][1], x[1]), x[0][2])).groupByKey().mapValues(list).map(lambda x: ((x[0][0], x[0][1]), (x[0][2], x[1]))).reduceByKey(max).map(lambda x: ((x[0][0], x[0][1], x[1][0]), x[1][1])).flatMapValues(lambda x: x).map(lambda x: (x[0][0], x[0][1], x[1], x[0][2])).sortBy(lambda x: (x[0], x[1]))

Query_6_result = Query_6.take(100)

tac = time()
dts.append(tac - tic)

with open("../outputs/RDD_Queries.txt",'a', encoding="utf-8") as output_f:
    output_f.write(55*"-"+"\nQuery 6 - RDD Version \n"+55*"-"+"\n")
    for row in list(Query_6_result):
        itm = row
        output_f.write("{} {} {} {} \n".format(itm[0], itm[1], itm[2], itm[3]))
with open("../outputs/RDD_times.csv",'a') as times_f:
    times_f.write("Query 6, \n".format(dts_a[5]))