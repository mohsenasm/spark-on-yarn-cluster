FROM bde2020/hadoop-base:2.0.0-hadoop3.1.1-java8

LABEL maintainer="m.m.asemanmanzar@gmail.com"

RUN printf "deb http://archive.debian.org/debian/ jessie main\ndeb-src http://archive.debian.org/debian/ jessie main\ndeb http://security.debian.org jessie/updates main\ndeb-src http://security.debian.org jessie/updates main" > /etc/apt/sources.list
RUN sed -i 's;http://archive.debian.org/debian/;http://deb.debian.org/debian/;' /etc/apt/sources.list

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python-pip && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3-pip wget && rm -rf /var/lib/apt/lists/*

RUN printf "<configuration>\n</configuration>\n" > /etc/hadoop/capacity-scheduler.xml \
    && sed -i '/configure \/etc\/hadoop\/mapred-site.xml mapred MAPRED_CONF/ a configure /etc/hadoop/capacity-scheduler.xml capsched CAP_SCHED_CONF' /entrypoint.sh \
    && sed -i 's/addProperty \/etc\/hadoop\/\$module-site.xml \$name \"\$value\"/addProperty \$path \$name \"\$value\"/g' /entrypoint.sh

ENV SPARK_VERSION=2.4.1
ENV HADOOP_VERSION_FOR_DOWNLOAD=2.7

RUN wget http://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION_FOR_DOWNLOAD}.tgz && \
    tar zxvf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION_FOR_DOWNLOAD}.tgz && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION_FOR_DOWNLOAD}.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION_FOR_DOWNLOAD} /opt/spark && \
    echo "export PATH=$PATH:/opt/spark/bin" >> /root/.bashrc && \
    echo "export SPARK_HOME=/opt/spark" >> /root/.bashrc

RUN  echo "export PYSPARK_PYTHON=python3" >> /root/.bashrc

# derby.system.home => https://www.ibm.com/support/knowledgecenter/en/SS3H8V_1.1.0/com.ibm.izoda.v1r1.azka100/topics/azkic_t_updconfigfiles.htm
RUN mkdir /tmp/spark-events && echo '\
spark.executor.memory           4g \n\
spark.eventLog.enabled          true \n\
spark.eventLog.dir              hdfs:///spark-history \n\
spark.history.fs.logDirectory   hdfs:///spark-history \n\
spark.yarn.historyServer.address 0.0.0.0:18080 \n\
spark.history.ui.port 18080 \n\
spark.hadoop.yarn.timeline-service.enabled false \n\
spark.driver.extraJavaOptions -Dderby.system.home=/spark-derby-system \n\
' > /opt/spark/conf/spark-defaults.conf

ADD setup-history-server.sh /usr/local/bin
COPY scripts /root/scripts

WORKDIR "/opt/spark"
