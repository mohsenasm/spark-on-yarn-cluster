FROM bde2020/hadoop-namenode:2.0.0-hadoop3.1.1-java8

LABEL maintainer="m.m.asemanmanzar@gmail.com"

RUN printf "<configuration>\n</configuration>\n" > /etc/hadoop/capacity-scheduler.xml \
    && sed -i '/configure \/etc\/hadoop\/mapred-site.xml mapred MAPRED_CONF/ a configure /etc/hadoop/capacity-scheduler.xml capsched CAP_SCHED_CONF' /entrypoint.sh \
    && sed -i 's/addProperty \/etc\/hadoop\/\$module-site.xml \$name \"\$value\"/addProperty \$path \$name \"\$value\"/g' /entrypoint.sh
