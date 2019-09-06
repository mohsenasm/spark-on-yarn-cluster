#!/usr/bin/python3

import subprocess
import sys
import datetime

def log(msg):
    print(str(msg) + "\r", flush=True)
    with open("stdout.txt","a") as out:
        out.write(str(msg) + "\n")

def print_time():
    log(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def popen_str(command_str):
    command = command_str.split()
    return popen(command)

def popen(command):
    with open("stdout.txt","ab") as out, open("stderr.txt","ab") as err:
        # log(command)
        return subprocess.Popen(command, stdout=out, stderr=err)

def run_the_cluster():
    up = popen_str("docker-compose -f spark-client-with-tpcds-docker-compose.yml up -d --build")
    log("- docker-compose up wating ...")
    up.wait()
    log("+ system is up with exitcode => {}".format(up.returncode))

def generate_tpc_ds_for_scales(scales):
    wait_list = []

    copy_queries = popen_str("docker-compose -f spark-client-with-tpcds-docker-compose.yml run tpc-ds /run.sh copy_queries")
    wait_list.append(("copy_queries", copy_queries))

    for scale in scales:
        gen_data = popen_str("docker-compose -f spark-client-with-tpcds-docker-compose.yml run tpc-ds /run.sh gen_data {}".format(scale))
        gen_ddl = popen_str("docker-compose -f spark-client-with-tpcds-docker-compose.yml run tpc-ds /run.sh gen_ddl {}".format(scale))

        wait_list.append(("gen_data {}".format(scale), gen_data))
        wait_list.append(("gen_ddl {}".format(scale), gen_ddl))

    for msg, process in wait_list:
        log("- {msg} wating ...".format(msg=msg))
        process.wait()
        log("+ {msg} returned with exitcode => {exitcode}".format(msg=msg, exitcode=process.returncode))

spark_client_command = "docker-compose -f spark-client-with-tpcds-docker-compose.yml run spark-client "

def copy_to_hdfs(scales):
    for scale in scales:
        mkdir = popen_str(spark_client_command
         + 'hdfs dfs -mkdir -p /tpc-ds-files/data')
        log("- copy_data({}).mkdir wating ...".format(scale))
        mkdir.wait()
        log("+ copy_data({}).mkdir retured with exitcode => {}".format(scale, mkdir.returncode))

        copy_data = popen_str(spark_client_command
         + 'hdfs dfs -copyFromLocal /tpc-ds-files/data/csv_{scale} /tpc-ds-files/data/csv_{scale}'.format(scale=scale))
        log("- copy_data({}) wating ...".format(scale))
        copy_data.wait()
        log("+ copy_data({}) retured with exitcode => {}".format(scale, copy_data.returncode))

    mkdir = popen_str(spark_client_command
     + 'hdfs dfs -mkdir -p /tpc-ds-files/pre_generated_queries')
    log("- copy_queries.mkdir wating ...")
    mkdir.wait()
    log("+ copy_queries.mkdir retured with exitcode => {}".format(mkdir.returncode))

    copy_queries = popen_str(spark_client_command
     + 'hdfs dfs -copyFromLocal /tpc-ds-files/pre_generated_queries /tpc-ds-files/')
    log("- copy_queries wating ...")
    copy_queries.wait()
    log("+ copy_queries retured with exitcode => {}".format(copy_queries.returncode))

def setup_history_server():
    p = popen_str(spark_client_command
     + 'setup-history-server.sh')
    log("- setup-history-server wating ...")
    p.wait()
    log("+ setup-history-server retured with exitcode => {}".format(p.returncode))

def create_parquet_files(scale):
    check_exist = popen_str(spark_client_command
     + 'hdfs dfs -mkdir /tpc-ds-files/data/parquet_{scale}'.format(scale=scale)).wait()
    if str(check_exist) == "0":
        mkdir = popen_str(spark_client_command
         + 'hdfs dfs -mkdir -p /tpc-ds-files/data/parquet_{scale}'.format(scale=scale))
        log("- create_parquet_files({}).mkdir wating ...".format(scale))
        mkdir.wait()
        log("+ create_parquet_files({}).mkdir retured with exitcode => {}".format(scale, mkdir.returncode))

        parquet = popen_str(spark_client_command
         + '/opt/spark/bin/spark-sql --master yarn --deploy-mode client -f /tpc-ds-files/ddl/tpcds_{scale}.sql'.format(scale=scale))
        log("- create_parquet_files({}) wating ...".format(scale))
        parquet.wait()
        log("+ create_parquet_files({}) retured with exitcode => {}".format(scale, parquet.returncode))
    else:
        log("+ create_parquet_files({}) skipped".format(scale))

def run_benchmark(query, scale):
    run = popen_str(spark_client_command
     + '/opt/spark/bin/spark-submit --master yarn --deploy-mode client /root/scripts/query.py -s {scale} -hf /tpc-ds-files/pre_generated_queries/query{query}.sql --name query{query}_cluster_{scale}G'.format(query=query, scale=scale))

    log("- run_benchmark({}, {}) wating ...".format(query, scale))
    run.wait()
    log("+ run_benchmark({query}, {scale}) returned with exitcode => {exitcode}".format(query=query, scale=scale, exitcode=run.returncode))

def copy_history():
    copy_to_container = popen_str(spark_client_command
     + 'hdfs dfs -copyToLocal /spark-history/* /spark-history/')
    log("- copy_history.to_container wating ...")
    copy_to_container.wait()
    log("+ copy_history.to_container returned with exitcode => {exitcode}".format(exitcode=copy_to_container.returncode))

    container_id = subprocess.check_output("docker-compose -f spark-client-with-tpcds-docker-compose.yml ps -q spark-client".split()).decode("utf-8").strip()

    copy_to_host = popen_str("docker cp {}:/spark-history .".format(container_id))
    log("- copy_history wating ...")
    copy_to_host.wait()
    log("+ copy_history returned with exitcode => {exitcode}".format(exitcode=copy_to_host.returncode))

def main():
    scales = sys.argv[1:]
    queries = [5, 19, 26, 40, 52]

    print_time() # log time
    run_the_cluster()
    print_time() # log time
    generate_tpc_ds_for_scales(scales)
    print_time() # log time
    copy_to_hdfs(scales)
    print_time() # log time
    setup_history_server()
    for scale in scales:
        print_time() # log time
        create_parquet_files(scale)
    for scale in scales:
        for query in queries:
            print_time() # log time
            run_benchmark(query, scale)
    print_time() # log time
    copy_history()
    print_time() # log time


if __name__ == "__main__":
    main()
