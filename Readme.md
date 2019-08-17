# Spark On Yarn Cluster

## 0. Disclaimer

This is a work-in-progress project. (WIP)

## 1. Test Yarn+HDFS with Wordcount

0. First run the cluster and go into the resourcemanager container: `docker-compose -f hadoop-docker-compose.yml up -d && docker-compose -f hadoop-docker-compose.yml exec resourcemanager bash`
1. Then copy a sample file for the wordcount application: `hdfs dfs -mkdir -p /in/ && hdfs dfs -copyFromLocal /opt/hadoop-3.1.1/README.txt /in/`
2. Run the wordcount application on the cluster: `yarn jar /opt/hadoop-3.1.1/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.1.1.jar wordcount /in /out`
3. See the output with `hdfs dfs -cat /out/*` and check hadoop history server on http://localhost:8188
4. Shutdown the cluster: `docker-compose -f hadoop-docker-compose.yml down -v`

## 2. Test Spark+Yarn in cluster/client mode with SparkPi

0. First run the cluster: `docker-compose -f spark-client-docker-compose.yml up -d --build`
1. Then go into the spark container: `docker-compose -f spark-client-docker-compose.yml run -p 18080:18080 spark-client bash`
2. Start the history server: `setup-history-server.sh`
3. Run the SparkPi application on the yarn cluster: `./bin/spark-submit --class org.apache.spark.examples.SparkPi --master yarn --deploy-mode cluster examples/jars/spark-examples*.jar 3` and see run history on http://localhost:18080
4. _optional_ Run the SparkPi application in **client mode** on the yarn cluster: `./bin/spark-submit --class org.apache.spark.examples.SparkPi --master yarn --deploy-mode client examples/jars/spark-examples*.jar 3` and see run history on http://localhost:18080
5. Shutdown the cluster: `docker-compose -f spark-client-docker-compose.yml down -v`

## 3. Run TPC-DS on Spark+Yarn in client mode
0. First run the cluster: `docker-compose -f spark-client-docker-compose.yml up -d --build`
1. Then go into the spark container: `docker-compose -f spark-client-docker-compose.yml run -p 18080:18080 -v /home/ubuntu/tpcds-kit:/opt/spark/tpcds-kit spark-client bash`
2. Start the history server: `setup-history-server.sh`
3. Get TPC-DS Files (skip this step if already created)
```
apt-get update && apt-get install -y gcc make flex bison byacc git
git clone https://github.com/gregrahn/tpcds-kit.git
cd tpcds-kit/tools
make OS=LINUX
mkdir -p /tpc-ds-data
./dsdgen -SCALE 1 -DIR /tpc-ds-data
mkdir -p /tpc-ds-query
./dsqgen -DIRECTORY ../query_templates -INPUT ../query_templates/templates.lst -SCALE 1 -VERBOSE Y -QUALIFY Y -OUTPUT_DIR /tpc-ds-query
```
4. Create Tables
```
cd tpcds-kit/tools/
spark-sql --master yarn --deploy-mode client -f tpcds.sql
```
5. to be continued!

## Web Tools
* namenode -> http://localhost:9870
* spark history -> http://localhost:18080
* hadoop history -> http://localhost:8188
