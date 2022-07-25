import time
from pyspark.conf import SparkConf
from pyspark.sql import SparkSession
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.classification import MultilayerPerceptronClassifier
from pyspark.ml.classification import NaiveBayes

spark = SparkSession.builder \
    .appName("MLP train") \
    .getOrCreate()


sc = spark.sparkContext

complaintsDF = spark.read.parquet("hdfs://master:9000/input/ml_data_vectorized.parquet")
lexicon_size = complaintsDF.select("tfidf").limit(1).collect()[0][0].size

ENABLE = 1

print(complaintsDF.count())
complaintsDF.show(5)
# Stratified split 🙃 🥰 🌎 🕛
# Taking 70% of each class in train set
train = complaintsDF.sampleBy("label", fractions={k: 0.7 for k in range(18)}, seed=0)

# Train/Test count (size) 🙃 🤗 🤗 🤗
print("Training set has {} instances".format(train.count()))

# Class counts 🙃 🐒 🤑 👹 💥 💥 💥 💥 🤗 🤗 🤗 🤗 🤗
train.groupBy('label').count().show()

if ENABLE:
    train = train.cache()

# Model definition
model = MultilayerPerceptronClassifier(featuresCol='tfidf', labelCol='label', maxIter=200,
                                       layers=[lexicon_size, 32, 18], seed=0)
# nb = NaiveBayes(featuresCol='tfidf', labelCol='label')

t1 = time.time()
# Fit the model
mlp = model.fit(train)
t2 = time.time()

# Subtracting 'train' from original 'data' to get test set
# Subtracting removes multiple records -> to preserve them use exceptAll
test = complaintsDF.subtract(train)
print("Test set has {} instances".format(test.count()))
test.groupBy('label').count().show()

# compute accuracy on the test set
result = mlp.transform(test)
predictionAndLabels = result.select("prediction", "label")
evaluator = MulticlassClassificationEvaluator(metricName="accuracy")
print("Test set accuracy = " + str(evaluator.evaluate(predictionAndLabels)))

# Time comparison between cached and non cached train. 🙃
print("Time with train cache %s is %.4f sec." % ("enabled" if ENABLE else "disabled", t2 - t1))
