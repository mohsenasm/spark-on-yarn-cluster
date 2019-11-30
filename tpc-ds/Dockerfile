# FROM bde2020/hadoop-base:2.0.0-hadoop3.1.1-java8
#
# RUN printf "deb http://archive.debian.org/debian/ jessie main\ndeb-src http://archive.debian.org/debian/ jessie main\ndeb http://security.debian.org jessie/updates main\ndeb-src http://security.debian.org jessie/updates main" > /etc/apt/sources.list
#
# RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
#     python-pip && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
#     python3-pip wget gcc make flex bison byacc build-essential aptitude libstdc++6 bash && rm -rf /var/lib/apt/lists/*

FROM debian:9

LABEL maintainer="m.m.asemanmanzar@gmail.com"

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python-pip && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3-pip wget gcc make flex bison byacc build-essential aptitude libstdc++6 bash && rm -rf /var/lib/apt/lists/*

COPY tpcds-kit /tpcds-kit
WORKDIR /tpcds-kit
RUN cd /tpcds-kit/tools && make OS=LINUX

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    nano less && rm -rf /var/lib/apt/lists/*

COPY pre_generated_queries /pre_generated_queries

COPY gen_ddl.py /opt/gen_ddl.py
COPY gen_ddl_csv.py /opt/gen_ddl_csv.py
COPY run.sh /run.sh
RUN chmod +x /run.sh
