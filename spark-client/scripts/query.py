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

    # get sqlText
    if args.query is not None:
        sqlText = args.query
    elif args.local_file is not None:
        sqlText = read_local_file(args.local_file)
    elif args.hdfs_file is not None:
        sqlText = read_hdfs_file(args.hdfs_file)
        # print(sqlText)
    else:
        raise Exception('should provide one of arguments.')
        # sqlText = "SELECT * from (SELECT count(*) from store_returns)"

    # load tables
    Path = sc._gateway.jvm.org.apache.hadoop.fs.Path
    FileSystem = sc._gateway.jvm.org.apache.hadoop.fs.FileSystem
    fs = FileSystem.get(sc._jsc.hadoopConfiguration())
    list_status = fs.listStatus(Path('/tpc-ds-files/data/parquet'))
    for folder in list_status:
        path = str(folder.getPath())
        name = str(folder.getPath().getName())
        spark.read.parquet(path).createOrReplaceTempView(name)

    # exec query
    spark.sql(sqlText).show()

    spark.stop()


# parse args & get query text
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="Name of the Application")
parser.add_argument("-hf", "--hdfs_file", help="Query File Address in HDFS")
parser.add_argument("-lf", "--local_file", help="Query File Address in Local File System")
parser.add_argument("-q", "--query", help="Query Text")
args = parser.parse_args()

run()
