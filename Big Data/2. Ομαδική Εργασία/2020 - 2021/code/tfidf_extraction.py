
import math
from pyspark.sql import SparkSession
from pyspark.ml.linalg import SparseVector
from pyspark.ml.feature import StringIndexer

spark = SparkSession.builder \
    .appName("tf-idf extraction") \
    .getOrCreate()

sc = spark.sparkContext

complaints = sc.textFile("hdfs://master:9000/input/complaints_clean.csv")

lexicon_size = 500  # max lexicon size 107302


def splitter(line):
    line = line.split(',')[1:]
    line[1] = line[1].rstrip("\n")
    return line


complaints = complaints.map(lambda x: splitter(x))

most_common_words = complaints. \
    flatMap(lambda x: x[1].split(" ")). \
    map(lambda x: (x, 1)). \
    reduceByKey(lambda x, y: x + y). \
    sortBy(lambda x: x[1], ascending=False).map(lambda x: x[0]).take(lexicon_size)

broad_com_words = sc.broadcast(most_common_words)

# (label, list_of_sentence_words_in_lexicon) MAP
# ((label, list_of_sentence_words_in_lexicon), sentence_index) ZIP
# ((word, label, sentence_index), 1) flatMap
# ((word, label, sentence_index), word_count_in_sentence) Reduce
# ((word, label, sentence_index), (word_count_in_sentence, word_index_in_lexicon)) Map
# ((sentence_index, label), [(word_index_in_lexicon, word_count_in_sentence)]) Map
# ((sentence_index, label), listof((word_index_in_lexicon, word_count_in_sentence))) RBK
# (label, sorted_on_word_index_in_lexicon_listof((word_index_in_lexicon, word_count_in_sentence)))
# values are like this [(idx1,count1),(idx2,count2),...]
# (label, SparseVector(lexicon_size, list_of(word_index_in_lexicon), list_of(word_frequencies_in_sentence)))

list_of_acummulators = [spark.sparkContext.accumulator(0) for i in range(lexicon_size)]

# lambda x: y[0] for y in x[0]
def addition(list_of_indices):
    global list_of_acummulators
    for ind in list_of_indices:
        list_of_acummulators[ind].add(1)


texts_with_words_in_lexicon = complaints.map(lambda x: (x[0], x[1].split(" "))). \
    map(lambda x: (x[0], [y for y in x[1] if y in broad_com_words.value])). \
    filter(lambda x: len(x[1]) != 0)

N = texts_with_words_in_lexicon.count()

word_counts = texts_with_words_in_lexicon. \
    zipWithIndex(). \
    flatMap(lambda x: [((y, x[0][0], x[1]), 1) for y in x[0][1]]). \
    reduceByKey(lambda x, y: x + y). \
    map(lambda x: (x[0], (x[1], broad_com_words.value.index(x[0][0])))). \
    map(lambda x: ((x[0][2], x[0][1]), [(x[1][1], x[1][0])])). \
    reduceByKey(lambda x, y: x + y). \
    map(lambda x: (x[0][1], sorted(x[1], key=lambda y: y[0])))

word_counts.foreach(lambda x: addition(y[0] for y in x[1]))

df = [y.value for y in list_of_acummulators]
df = sc.broadcast(df)

complaints_tfidf = word_counts. \
    map(lambda x: (
    x[0], SparseVector(lexicon_size, [y[0] for y in x[1]],
                       [y[1] / sum([y[1] for y in x[1]]) * math.log(N / df.value[y[0]]) for y in x[1]])))

complaintsDF = complaints_tfidf.toDF(["Category_label", "tfidf"])

# Use StringIndexer to transform Category into integers

stringIndexer = StringIndexer(inputCol="Category_label", outputCol="label")
stringIndexer.setHandleInvalid("skip")
stringIndexerModel = stringIndexer.fit(complaintsDF)
complaintsDF = stringIndexerModel.transform(complaintsDF)
complaintsDF.write.parquet("hdfs://master:9000/input/ml_data_vectorized.parquet")



