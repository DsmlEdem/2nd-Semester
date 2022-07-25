import time
import re

from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext

spark = SparkSession.builder \
    .appName("ML-rdd") \
    .getOrCreate()

sc = spark.sparkContext
sqlContext = SQLContext(sc)

complaints = sc.textFile("hdfs://master:9000/input/customer_complaints.csv")
stop_words = set(stopwords.words('english'))
stop_words.add("xxxx")
stop_words = sc.broadcast(stop_words)


def splitter(line):
    return line.split(",")


def data_cleaning(line):
    """
    Function used for data cleaning. Remove empty records
    :param line: Line of csv containing info for each record
    :return:
    """
    if len(line) == 3 and (line[0].startswith("201")) and (line[1] != "") and (line[2] != ""):
        return True
    return False


def decontracted(phrase):
    # specific
    phrase = re.sub(r"won\'t", "will not", phrase)
    phrase = re.sub(r"can\'t", "can not", phrase)

    # general
    phrase = re.sub(r"n\'t", " not", phrase)
    phrase = re.sub(r"\'re", " are", phrase)
    phrase = re.sub(r"\'s", " is", phrase)
    phrase = re.sub(r"\'d", " would", phrase)
    phrase = re.sub(r"\'ll", " will", phrase)
    phrase = re.sub(r"\'t", " not", phrase)
    phrase = re.sub(r"\'ve", " have", phrase)
    phrase = re.sub(r"\'m", " am", phrase)
    return phrase


def check_tokens(line):
    return len(line[2]) != 0


def preprocess_text(line):
    """
    Preprocessing for complaint (lowercase -> remove urls -> remove contraction ->
    Tokenize -> Lemmatize -> Remove stopwords)
    :param line: CSV line containing Date,Category,Complaint
    :return: A list of tokens for the corresponding complaint
    """

    complaint = line[2]
    complaint = complaint.lower()
    complaint = re.sub(r"https?:\/\/t.co\/[A-Za-z0-9]+", "", complaint)  # remove urls
    complaint = decontracted(complaint)  # fix contractions
    tokenizer = RegexpTokenizer(pattern='[a-z]+')  # keep only lowercase letters
    complaint = tokenizer.tokenize(complaint)
    lemmatizer = WordNetLemmatizer()
    complaint = [lemmatizer.lemmatize(w) for w in complaint]
    # remove stopwords
    complaint = [w for w in complaint if w not in stop_words.value and len(w) > 2]
    line[2] = " ".join(complaint)
    return line


complaints = complaints.map(lambda x: splitter(x)). \
    filter(lambda x: data_cleaning(x)). \
    map(lambda x: preprocess_text(x)). \
    filter(lambda x: check_tokens(x))  # date, category, complaint

# save to df an then csv
df = sqlContext.createDataFrame(complaints, ["Date", "Category", "Complaint"])
df.coalesce(1).write.format('com.databricks.spark.csv').options(header='false'). \
    save("hdfs://master:9000/input/complaints_clean.csv")

