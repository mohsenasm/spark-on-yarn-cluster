FROM hseeberger/scala-sbt:11.0.4_1.3.2_2.13.1

LABEL maintainer="m.m.asemanmanzar@gmail.com"

RUN sed -i 's;http://archive.debian.org/debian/;http://deb.debian.org/debian/;' /etc/apt/sources.list
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python-pip && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3-pip wget gcc make flex bison byacc build-essential aptitude libstdc++6 bash && rm -rf /var/lib/apt/lists/*

ENV SPARK_VERSION=2.4.1
ENV HADOOP_VERSION_FOR_DOWNLOAD=2.7

RUN wget http://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION_FOR_DOWNLOAD}.tgz && \
    tar zxvf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION_FOR_DOWNLOAD}.tgz && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION_FOR_DOWNLOAD}.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION_FOR_DOWNLOAD} /opt/spark && \
    echo "export PATH=$PATH:/opt/spark/bin" >> /root/.bashrc && \
    echo "export PATH=$PATH:/opt/spark/sbin" >> /root/.bashrc && \
    echo "export SPARK_HOME=/opt/spark" >> /root/.bashrc

RUN echo "export PYSPARK_PYTHON=python3" >> /root/.bashrc

RUN mkdir /tmp/spark-events && echo '\
spark.eventLog.enabled          true \n\
spark.eventLog.dir              /spark-history \n\
spark.history.fs.logDirectory   /spark-history \n\
' > /opt/spark/conf/spark-defaults.conf

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    procps && rm -rf /var/lib/apt/lists/*

WORKDIR "/opt/spark"
