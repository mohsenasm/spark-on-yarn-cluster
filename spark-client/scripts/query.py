from pyspark.sql import SparkSession
import sys
import argparse
import subprocess

def read_hdfs_file(addr):
    cat = subprocess.Popen(["hadoop", "fs", "-cat", addr], stdout=subprocess.PIPE)
    return "".join([line.decode("utf-8")  for line in cat.stdout])

def read_local_file(addr):
    with open(addr, 'r') as content_file:
        return content_file.read()

def run():
    spark = SparkSession.builder.appName(args.name).getOrCreate()
    sc = spark.sparkContext

    # get sqlTexts
    if args.query is not None:
        sqlTexts = [args.query]
    elif (args.local_file is not None) and (len(args.local_file) > 0):
        sqlTexts = [read_local_file(f) for f in args.local_file]
    elif (args.hdfs_file is not None) and (len(args.hdfs_file) > 0):
        sqlTexts = [read_hdfs_file(f) for f in args.hdfs_file]
    else:
        raise Exception('should provide one of arguments.')
        # sqlTexts = ["SELECT * from (SELECT count(*) from store_returns)"]

    # load tables
    Path = sc._gateway.jvm.org.apache.hadoop.fs.Path
    FileSystem = sc._gateway.jvm.org.apache.hadoop.fs.FileSystem
    fs = FileSystem.get(sc._jsc.hadoopConfiguration())
    list_status = fs.listStatus(Path('/tpc-ds-files/data/parquet_{}'.format(args.scale)))
    for folder in list_status:
        path = str(folder.getPath())
        name = str(folder.getPath().getName())
        spark.read.parquet(path).createOrReplaceTempView(name)

    # exec queries
    print("-"*10)
    for sqlText in sqlTexts:
        spark.sql(sqlText).collect()
        print("-"*10)

    spark.stop()


# parse args & get query text
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", default="query.py", help="Name of the Application")
parser.add_argument("-s", "--scale", default="1", help="Scale of the generated data")
parser.add_argument("-hf", "--hdfs_file", action='append', help="Query File Address in HDFS")
parser.add_argument("-lf", "--local_file", action='append', help="Query File Address in Local File System")
parser.add_argument("-q", "--query", help="Query Text")
args = parser.parse_args()

run()
