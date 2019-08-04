FROM bde2020/spark-master:2.4.3-hadoop2.7

RUN apk add --no-cache perl

WORKDIR "/spark"

ADD entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
