FROM bde2020/hadoop-base:2.0.0-hadoop3.1.1-java8

RUN printf "deb http://archive.debian.org/debian/ jessie main\ndeb-src http://archive.debian.org/debian/ jessie main\ndeb http://security.debian.org jessie/updates main\ndeb-src http://security.debian.org jessie/updates main" > /etc/apt/sources.list

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python-pip && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3-pip wget && rm -rf /var/lib/apt/lists/*

ENV SPARK_VERSION=2.4.1
ENV HADOOP_VERSION_FOR_DOWNLOAD=2.7

RUN wget http://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION_FOR_DOWNLOAD}.tgz && \
    tar zxvf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION_FOR_DOWNLOAD}.tgz && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION_FOR_DOWNLOAD}.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION_FOR_DOWNLOAD} /opt/spark && \
    echo "export PATH=$PATH:/opt/spark/bin" >> /root/.bashrc && \
    echo "export SPARK_HOME=/opt/spark" >> /root/.bashrc

RUN mkdir /tmp/spark-events && echo '\
spark.eventLog.enabled          true \n\
spark.eventLog.dir              /tmp/spark-events \n\
spark.history.fs.logDirectory   /tmp/spark-events \n\
spark.hadoop.yarn.timeline-service.enabled false' > /opt/spark/conf/spark-defaults.conf

WORKDIR "/opt/spark"
