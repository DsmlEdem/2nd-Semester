import time
from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer
from pyspark.ml.classification import MultilayerPerceptronClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from nltk.corpus import stopwords 

spark = SparkSession.builder.appName("mlp-train").getOrCreate() # Get spark session
sc = spark.sparkContext
stop_words = stopwords.words('english')
spark.sparkContext.setLogLevel('WARN')
spark.catalog.clearCache()

lex_file = "hdfs://master:9000/project2/tfidf-60.parquet"
lexicon_size = int(lex_file.split("-")[1].split(".")[0])

df = spark.read.load(lex_file)
stringIndexer = StringIndexer(inputCol='category', outputCol='label')
stringIndexer.setHandleInvalid('skip')
stringIndexerModel = stringIndexer.fit(df)
df = stringIndexerModel.transform(df)

# Grab unique labels
uniq = df.select('label').distinct().collect()

# Split Ratio for each Label
fractions = {i: 0.8 for i in range(len(uniq)+1)}

# Split to train-test
train_set = df.sampleBy('label', fractions=fractions, seed=25).cache()
test_set = df.subtract(train_set)

# Get number of documents for each set
print('\n\nSize of train set: ', train_set.count(), '\n\n')
print('\n\nSize of test set: ', test_set.count(), '\n\n')

# Samples per Category for each set
train_set.groupBy('category').count().show()
test_set.groupBy('category').count().show()

# input layer:k size, output layer:unique_cat size
layers = [lexicon_size, 200, len(uniq)]

# Trainer
trainer = MultilayerPerceptronClassifier(maxIter=100, layers=layers, blockSize=64, seed=25)


"""
MODEL 
TRAINING 
WITHOUT 
CACHING

"""
print('\n Starting Training of the model without caching:')
start_time = time.time()
model = trainer.fit(train_set)
end_time = time.time()
print('\n\n--- Time Elapsed for Training without caching: {:0.2f} seconds ---\n\n'.format(end_time - start_time))

# compute accuracy on the test set
result = model.transform(test_set)
predictionAndLabels = result.select('prediction', 'label')
evaluator = MulticlassClassificationEvaluator(metricName='accuracy')
print('\nTest set accuracy = {:0.2f} %\n'.format(evaluator.evaluate(predictionAndLabels) * 100))



"""
MODEL 
TRAINING 
WITH
CACHING

"""

train_set = train_set.cache()
print('\n Starting Training of the model with caching:')
start_time_ = time.time()
cached_model = trainer.fit(train_set)
end_time_ = time.time()
print('\n\n--- Time Elapsed for Training with caching: {:0.2f} seconds ---\n\n'.format(end_time_ - start_time_))

# compute accuracy on the test set
result_ = cached_model.transform(test_set)
predictionAndLabels_ = result_.select('prediction', 'label')
evaluator = MulticlassClassificationEvaluator(metricName='accuracy')
print('\nTest set accuracy = {:0.2f} %\n'.format(evaluator.evaluate(predictionAndLabels_) * 100))







# Stop the session
spark.stop()





