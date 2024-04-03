import re
from pyspark.sql import SparkSession
from pprint import pprint

sc = SparkSession \
    .builder \
    .appName("Part 1 RDD query 5 execution") \
    .getOrCreate() \
    .sparkContext

def no_null_fields(rec):
    if any(not field for field in rec):
        return False
    return True

def html_to_urls(html):
    url_re = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return url_re.findall(html)

def main():
    warc = sc.textFile("hdfs://master:9000/user/user/files/warc.csv") \
                .map(lambda x: x.split(",")) \
                .filter(no_null_fields)

    urls_in_html = warc.flatMap(lambda x: [(x[5], url) for url in html_to_urls(x[7])])
    url_counts = urls_in_html.map(lambda x: (x[1], 1)).reduceByKey(lambda a, b: a + b)

    pprint(url_counts.sortBy(lambda x: -x[1]).take(10))

if __name__ == "__main__":
    main()
