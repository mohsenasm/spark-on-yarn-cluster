FROM bde2020/hadoop-resourcemanager:2.0.0-hadoop3.1.1-java8

LABEL maintainer="m.m.asemanmanzar@gmail.com"

RUN printf "deb http://archive.debian.org/debian/ jessie main\ndeb-src http://archive.debian.org/debian/ jessie main\ndeb http://security.debian.org jessie/updates main\ndeb-src http://security.debian.org jessie/updates main" > /etc/apt/sources.list

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python-pip && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3-pip wget && rm -rf /var/lib/apt/lists/*

RUN sed -i '/configure \/etc\/hadoop\/mapred-site.xml mapred MAPRED_CONF/ a configure /etc/hadoop/capacity-scheduler.xml capsched CAP_SCHED_CONF' /entrypoint.sh \
    && sed -i 's/addProperty \/etc\/hadoop\/\$module-site.xml \$name \"\$value\"/addProperty \$path \$name \"\$value\"/g' /entrypoint.sh
