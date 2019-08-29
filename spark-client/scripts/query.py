from pyspark.sql import SparkSession
import sys

spark = SparkSession.builder.appName("Spark-SQL-in-Python").getOrCreate()
sc = spark.sparkContext

Path = sc._gateway.jvm.org.apache.hadoop.fs.Path
FileSystem = sc._gateway.jvm.org.apache.hadoop.fs.FileSystem
fs = FileSystem.get(sc._jsc.hadoopConfiguration())
list_status = fs.listStatus(Path('/tpc-ds-files/data/parquet'))

for folder in list_status:
    path = str(folder.getPath())
    name = str(folder.getPath().getName())
    spark.read.parquet(path).createOrReplaceTempView(name)

sqlText = sys.argv[1]
# sqlText = "SELECT count(*) from store_returns"

spark.sql(sqlText).show()

spark.stop()
