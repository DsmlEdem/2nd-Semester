import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, DateType, TimestampType, ShortType
from pyspark.sql.types import IntegerType, LongType, StructField, StructType

spark = SparkSession.builder.appName('csvToParquet').getOrCreate()

artists_schema = StructType([
    StructField('artistId', LongType(), False),
    StructField('artistName', StringType(), True),
])

chart_artist_mapping_schema = StructType([
    StructField('songId', LongType(), False),
    StructField('artistId', LongType(), True),
])

charts_schema = StructType([
    StructField('songId', LongType(), False),
    StructField('title', StringType(), True),
    StructField('position', ShortType(), True),
    StructField('date', DateType(), True),
    StructField('countryId', LongType(), True),
    StructField('chartName', StringType(), True),
    StructField('movement', StringType(), True),
    StructField('streams', LongType(), True),
])

regions_schema = StructType([
    StructField('countryId', LongType(), False),
    StructField('countryName', StringType(), True),
])

it = [
    ('artists', artists_schema),
    ('chart_artist_mapping', chart_artist_mapping_schema),
    ('charts', charts_schema),
    ('regions', regions_schema),
]

for stem, schema in it:
    print(stem)
    
    df = spark.read.csv(
        'files/{}.csv'.format(stem),
        sep=',', header='false', schema=schema
    )
    df.write.save('files/{}.parquet'.format(stem))
    
    spark.read.parquet('files/{}.parquet'.format(stem)).show(2)
    print('=' * 40)


spark.stop()
