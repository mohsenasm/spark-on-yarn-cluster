from pyspark.sql import SparkSession
import sys
import argparse
import subprocess

spark = SparkSession.builder.appName("Spark-SQL-in-Python").getOrCreate()
sc = spark.sparkContext

# load tables
Path = sc._gateway.jvm.org.apache.hadoop.fs.Path
FileSystem = sc._gateway.jvm.org.apache.hadoop.fs.FileSystem
fs = FileSystem.get(sc._jsc.hadoopConfiguration())
list_status = fs.listStatus(Path('/tpc-ds-files/data/parquet'))
for folder in list_status:
    path = str(folder.getPath())
    name = str(folder.getPath().getName())
    spark.read.parquet(path).createOrReplaceTempView(name)

# parse args & get query text
parser = argparse.ArgumentParser()
parser.add_argument("-hf", "--hdfs_file", help="Query File")
parser.add_argument("-lf", "--local_file", help="Query File")
parser.add_argument("-q", "--query", help="Query Text")
args = parser.parse_args()
if args.query is not None:
    sqlText = args.query
elif args.local_file is not None:
    with open(args.local_file, 'r') as content_file:
        sqlText = content_file.read()
elif args.hdfs_file is not None:
    cat = subprocess.Popen(["hadoop", "fs", "-cat", args.hdfs_file], stdout=subprocess.PIPE)
    sqlText = "".join([line.decode("utf-8")  for line in cat.stdout])
    # print(sqlText)
else:
    raise Exception('should provide one of arguments.')

# exec query
# sqlText = "SELECT * from (SELECT count(*) from store_returns)"
spark.sql(sqlText).show()

spark.stop()
