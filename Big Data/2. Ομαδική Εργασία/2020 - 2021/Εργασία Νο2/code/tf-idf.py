import re
import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.ml.linalg import SparseVector
from pyspark.ml.feature import StringIndexer
from pyspark.ml.classification import MultilayerPerceptronClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from nltk.corpus import stopwords 
from math import log

	
lexicon_size = 70 # Define lexicon size 
spark = SparkSession.builder.appName("tfidf").getOrCreate() # Get spark session
sc = spark.sparkContext
spark.sparkContext.setLogLevel('WARN')
spark.catalog.clearCache()
stop_words = stopwords.words('english')


print('\nCleaning Data, removing stopwords etc.\n')
data = sc.textFile("hdfs://master:9000/project2/customer_complaints.csv")\
    .filter(lambda x: x.startswith("201"))\
    .map(lambda x: x.split(','))\
    .filter(lambda x: len(x) == 3)\
    .filter(lambda x: len(x[1].strip()) != 0 and len(x[2].strip()) != 0)\
    .map(lambda x: [x[1],re.sub(r'X{2,}','', x[2])])\
    .map(lambda x: [x[0],re.sub(r'[^A-Za-z ]', '', x[1]).strip().lower()])\
    .map(lambda x: [x[0], ' '.join([j for j in x[1].split() if j not in stop_words])])\
    .filter(lambda x: [x[0], x[1] is not None])


"""
Word Count to find lexicon

- First Keep Only the Complaints and then split at " "
- Map as (word,1)
- Reduce in order to count same words (word, #ofappearances)
- Sort by words with highest count
- Keep only the words, we don't need the counts.
- Keep lexicon_size most frequent words
"""
print("\nCreating the lexicon\n")
lexicon = data.flatMap(lambda x : x[1].split(" ")).\
                map(lambda x : (x, 1)).\
                reduceByKey(lambda x, y: x + y).\
		        sortBy(lambda x : x[1], ascending = False).\
                map(lambda x : x[0]).\
                take(lexicon_size)
print(lexicon)
# Broadcast to all workers
broad_lexicon = sc.broadcast(lexicon)

"""
Input: [label, comment]
1. Split comment into words 
    Output: (label, list_of_words_in_comment)
2. Keep only words that appear on the lexicon. 
    Output: (label, list_of_words_appearing_in_lexicon)
3. Filter null strings
    Output: ((label, list_of_words_in_lexicon),doc_index)
"""
print("\nKeeping words inside the lexicon only.\n")
keep = data.map(lambda x: (x[0], x[1].split(' '))).\
        map(lambda x: (x[0], [y for y in x[1] if y in broad_lexicon.value])).\
        filter(lambda x: x[1] != '').\
        zipWithIndex().\
        cache()

# release memory.
data.unpersist()
# Count number of total documents:
N = keep.count()
print('\nTotal Documents in Dataset: {}.\n'.format(N))

"""
Calculate IDF:
Input: ((label, list_of_words_in_lexicon),doc_index)
1. Bring into (word,1) form in order to count words
    Output: (word,1)
2. Reduce step
    Output: (word, #appearances_in_corpus)
3. IDF calculation. IDF = log(N/(#of_documents_the_word_appears_in))
    Output: (word, IDF)
"""
print('\nCalculating IDF\n')
idf = keep.\
    flatMap(lambda x: [(y, 1) for y in list(set(x[0][1]))]).\
    reduceByKey(lambda x, y: x+y).\
    map(lambda x: (x[0], log(N/x[1]))).collect()

# Broadcast it, so the workers can use it
shared_idf = sc.broadcast(idf)

""""
TF-IDF Calculation:
Input: ((label, list_of_words_in_lexicon),doc_index)
1. We need to count the appearances of a single word inside that document,
    so we need to calculate the length of words of that comment, while
    keeping the label and doc_id.
    Output: ((word, label, doc_id, comment_length), 1)
2. Reduce step to count appearances (count = number of word appearances in the comment)
    Output: ((word, label, doc_id, comment_length), count))
3. TF-IDF calculation, as tf = count/comment_length and
    we already have idf so we need to match the words.
    Output: ((word, label, doc_id), TFIDF))
4. We also need the word's index on the lexicon
    Output: ((word, label, doc_id), (word_id, TFIDF))
5.  Output: (doc_id, label), [word_id, TFIDF])
6.  Reduce step
    (doc_id, label), list_of([word_id, TFIDF]))
7. Sort by TFIDF value, drop doc_id
    Output: (label, sorted_list with word_index as key and tfidf metric value as value)
8. Final Step, return the requested sparse vector, with label as key.
    Output: (label, SparseVector(k,key:word_id - value:TFIDF))
"""
print("\nCalculating TFIDF\n")
tfidf = keep.\
    flatMap(lambda x: [((y, x[0][0], x[1], len(x[0][1])), 1) for y in x[0][1]]).\
    reduceByKey(lambda x, y: x+y).\
    map(lambda x: ((x[0][0], x[0][1], x[0][2]), (x[1]/x[0][3]) * [y[1] for y in shared_idf.value if y[0] == x[0][0]][0])).\
    map(lambda x: (x[0], (broad_lexicon.value.index(x[0][0]), x[1]))).\
    map(lambda x: ((x[0][2], x[0][1]), [x[1]])).\
    reduceByKey(lambda x, y: x+y).\
    map(lambda x: (x[0][1], sorted(x[1], key=lambda y: y[0]))).\
    map(lambda x: (x[0], SparseVector(lexicon_size, [y[0] for y in x[1]], [y[1] for y in x[1]])))

# Print Requested Outputs
print('\n\nRequested Outputs\n')
for i in tfidf.take(5):
    print(i)
print('\n')
print('\nWriting to parquet:\n')
df = tfidf.toDF(['category', 'features'])
df.write.parquet('hdfs://master:9000/project2/tfidf-{}.parquet'.format(int(lexicon_size)))