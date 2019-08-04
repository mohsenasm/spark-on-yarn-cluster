FROM bde2020/hadoop-base:2.0.0-hadoop3.1.1-java8

RUN apk add --no-cache perl

WORKDIR "/spark"

ADD entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
