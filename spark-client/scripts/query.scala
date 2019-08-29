// this script is incomplete!

import org.apache.hadoop.conf.Configuration
import org.apache.hadoop.fs.Path
import org.apache.hadoop.fs.FileSystem
import org.apache.spark.{SparkConf, SparkContext}

val fs = FileSystem.get(new Configuration())
val status = fs.listStatus(new Path("/tpc-ds-files/data/parquet"))

val conf = new SparkConf().setAppName("spark-sql-in-scala")
val sc = new SparkContext(conf)
val sqlContext = new org.apache.spark.sql.SQLContext(sc)
import sqlContext.implicits._

val parquetFiles = status.map(folder => {
    sqlContext.read.parquet(folder.getPath.toString)
  })

sqlText = "SELECT count(*) from store_returns"

sqlContext.sql(sqlText).show()

// val mergedFile = parquetFiles.reduce((x, y) => x.unionAll(y))
// parquetFileDF.createOrReplaceTempView("parquetFile")
// val namesDF = spark.sql("SELECT name FROM parquetFile WHERE age BETWEEN 13 AND 19")
// namesDF.map(attributes => "Name: " + attributes(0)).show()

// sqlContext.sql("SELECT count(*) from store_returns").show()
