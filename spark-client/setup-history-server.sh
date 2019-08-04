#!/bin/bash

hdfs dfs -mkdir /spark-history
hdfs dfs -chown -R spark:hadoop /spark-history
hdfs dfs -chmod -R 777 /spark-history

/opt/spark/sbin/start-history-server.sh
