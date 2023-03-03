# Spark On Yarn Cluster

[![Docker Build Status](https://travis-ci.org/mohsenasm/spark-on-yarn-cluster.svg?branch=master)](https://travis-ci.org/mohsenasm/spark-on-yarn-cluster)

This repo is used in this publication: 

M. M. Aseman-Manzar, S. Karimian-Aliabadi, R. Entezari-Maleki, B. Egger and A. Movaghar, "Cost-aware Resource Recommendation for DAG-based Big Data Workflows: An Apache Spark Case Study," in IEEE Transactions on Services Computing, 2022, doi: 10.1109/TSC.2022.3203010. https://ieeexplore.ieee.org/abstract/document/9894699

This repo is also helpful for parsing the history logs:

https://github.com/mohsenasm/Python-Spark-Log-Parser

## 1. Test Yarn+HDFS with Wordcount

1. First run the cluster and go into the resourcemanager container:  
`docker-compose -f hadoop-docker-compose.yml up -d && docker-compose -f hadoop-docker-compose.yml exec resourcemanager bash`
    1. Then copy a sample file for the wordcount application:  
    `hdfs dfs -mkdir -p /in/ && hdfs dfs -copyFromLocal /opt/hadoop-3.1.1/README.txt /in/`
    2. Run the wordcount application on the cluster:  
    `yarn jar /opt/hadoop-3.1.1/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.1.1.jar wordcount /in /out`
    3. See the output with:  
    `hdfs dfs -cat /out/*` and check hadoop history server on http://localhost:8188
2. Remove the cluster:  
`docker-compose -f hadoop-docker-compose.yml down -v`

## 2. Test Spark+Yarn in cluster/client mode with SparkPi

1. First run the cluster:  
`docker-compose -f spark-client-docker-compose.yml up -d --build`
2. Then go into the spark container:  
`docker-compose -f spark-client-docker-compose.yml run -p 18080:18080 spark-client bash`
    1. Start the history server:  
    `setup-history-server.sh`
    2. Run the SparkPi application on the yarn cluster:  
    `./bin/spark-submit --class org.apache.spark.examples.SparkPi --master yarn --deploy-mode cluster examples/jars/spark-examples*.jar 3`  
    and see run history on http://localhost:18080
    3. _optional_ Run the SparkPi application in **client mode** on the yarn cluster:  
    `./bin/spark-submit --class org.apache.spark.examples.SparkPi --master yarn --deploy-mode client examples/jars/spark-examples*.jar 3`  
    and see run history on http://localhost:18080
3. Remove the cluster:  
`docker-compose -f spark-client-docker-compose.yml down -v`

## 3. Run TPC-DS on Spark+Yarn

1. First run the cluster:  
`docker-compose -f spark-client-with-tpcds-docker-compose.yml up -d --build`
2. Then go into the tpc-ds container:  
`docker-compose -f spark-client-with-tpcds-docker-compose.yml run tpc-ds /run.sh bash`
    1. `/run.sh gen_data 1`
    2. `/run.sh copy_queries`
    <!-- + `/run.sh gen_queries` -> cannot be used in spark because of wrong templates-->
    3. `/run.sh gen_ddl 1` for using parquet
    4. `/run.sh gen_ddl_csv 1` for using csv
3. Then go into the spark container:  
`docker-compose -f spark-client-with-tpcds-docker-compose.yml run -p 18080:18080 spark-client bash`
    1. Start the history server:  
    `setup-history-server.sh`
    2. Copy data to HDFS:  
    `hdfs dfs -mkdir -p /tpc-ds-files/data/parquet_1 && hdfs dfs -copyFromLocal /tpc-ds-files/data/csv_1 /tpc-ds-files/data/csv_1`
    3. Create parquet tables (for steps 4, 5, 6 and 10):  
    `spark-sql --master yarn --deploy-mode client -f /tpc-ds-files/ddl/tpcds_1.sql --name create_db_scale_1`
    4. _optional_ Run sample query:  
    `spark-submit --master yarn --deploy-mode client /root/scripts/query.py -s 1 -q 'SELECT * from (SELECT count(*) from store_returns)' --name 'query for test database creation'`
    5. **(Client Mode)** Run a TPC-DS query from pre-generated queries with spark-submit:  
    `spark-submit --master yarn --deploy-mode client /root/scripts/query.py -s 1 -lf /tpc-ds-files/pre_generated_queries/query5.sql --name query5_client`
    6. **(Client Mode + spark-sql)** Run a TPC-DS query from pre-generated queries with spark-sql: `spark-sql --master yarn --deploy-mode client --conf spark.sql.crossJoin.enabled=true -database scale_1 -f /tpc-ds-files/pre_generated_queries/query26.sql --name query26_cluster`
    7. Create csv tables (for step 8):  
    `spark-sql --master yarn --deploy-mode client -f /tpc-ds-files/ddl/tpcds_1_csv.sql --name create_db_scale_1_csv`
    8. **(Client Mode + spark-sql + csv_database)** Run a TPC-DS query from pre-generated queries with spark-sql: `spark-sql --master yarn --deploy-mode client --conf spark.sql.crossJoin.enabled=true -database scale_1_csv -f /tpc-ds-files/pre_generated_queries/query26.sql --name query26_cluster`
    9. Copy TPC-DS pre-generated queries to HDFS:  
    `hdfs dfs -mkdir -p /tpc-ds-files/pre_generated_queries && hdfs dfs -copyFromLocal /tpc-ds-files/pre_generated_queries /tpc-ds-files/`
    10. **(Cluster Mode)** Run a TPC-DS query from pre-generated queries with spark-submit:  
    `spark-submit --master yarn --deploy-mode cluster /root/scripts/query.py -s 1 -hf /tpc-ds-files/pre_generated_queries/query40.sql -hf /tpc-ds-files/pre_generated_queries/query52.sql --name query40_and_query52_cluster`
4. Remove the cluster:  
`docker-compose -f spark-client-with-tpcds-docker-compose.yml down -v`

## 4. Run Multiple Samples of TPC-DS on Spark+Yarn

1. Run `python3 run_tpcds.py 1 3 5 10`. Then history will be on `hdfs:///spark-history` and on `./output/spark-history` in the host.
2. Remove the cluster:  
`docker-compose -f spark-client-with-tpcds-docker-compose.yml down -v`  

## 5. Run Multiple Samples of TPC-DS on Spark+Yarn in **Swarm Cluster**  

0. Change directory to the `swarm` directory in root of the project.  
1. Preparations:  
    1. Setup swarm manager with `docker swarm init --advertise-addr <the_manager_ip_address>`. This command will print a `docker swarm join` command, copy it.  
    2. Run the `join command` into each worker.  
    3. On the swarm manager, for each node, assign label `node-id`. (`docker node update --label-add node-id=1 node1_hostname`)  
    4. Update file `swarm/spark-swarm-client.yml`.  
2. Run swarm cluster with `docker stack deploy -c spark-swarm.yml tpcds` and wait until all services in `docker service ls` be running.  
3. Run `ADDITIONAL_SPARK_CONFIG="--num-executors 25 --executor-cores 1 --executor-memory 1G" USE_CSV="False" python3 run_tpcds_on_swarm.py 1 10 20 40 35 70 100 120 135 150`. Then history will be on `hdfs:///spark-history` and on `./output/spark-history` in the host.  
4. Remove the cluster:  
    1. Remove all services: `docker stack rm tpcds && docker-compose -f spark-swarm-client.yml down -v`  
    2. On each nodes:  
        * wait until `docker ps` prints no services.  
        * execute `docker ps && docker container prune && docker volume prune` and confirm `y`.  

## To See Progress in Swarm  
`docker service create --mount type=bind,source=/var/run/docker.sock,destination=/var/run/docker.sock -p 80:8080 -e PORT=8080 --constraint 'node.role == manager' --name swarm-dashboard charypar/swarm-dashboard
`

## Web Tools  
* namenode -> http://localhost:9870  
* spark history -> http://localhost:18080  
* hadoop history -> http://localhost:8188  
* swarm-dashboard -> http://localhost:80
