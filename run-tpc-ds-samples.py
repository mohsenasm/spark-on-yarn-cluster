#!/usr/bin/python3

import subprocess
import sys
import datetime

def log(msg):
    print(str(msg) + "\r\n", flush=True)

def print_time():
    log(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def popen_str(command_str):
    command = command_str.split()
    return popen(command)

def popen(command):
    with open("stdout.txt","ab") as out, open("stderr.txt","ab") as err:
        log(command)
        return subprocess.Popen(command, stdout=out, stderr=err)

def run_the_cluster():
    up = popen_str("docker-compose -f spark-client-with-tpcds-docker-compose.yml up -d --build")
    log("- wait for docker-compose up")
    up.wait()
    log("+ system is up with exitcode={}".format(up.returncode))

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
        log("- wait for {msg}".format(msg=msg))
        process.wait()
        log("+ {msg} returned with exitcode={exitcode}".format(msg=msg, exitcode=process.returncode))

spark_client_command = "docker-compose -f spark-client-with-tpcds-docker-compose.yml run spark-client "

def copy_to_hdfs():
    copy_data = popen_str(spark_client_command
     + 'hdfs dfs -mkdir -p /tpc-ds-files/data && hdfs dfs -copyFromLocal /tpc-ds-files/data/csv* /tpc-ds-files/data/')
    log("- wait for copy_data")
    copy_data.wait()
    log("+ copy_data retured with exitcode={}".format(copy_data.returncode))

    copy_queries = popen_str(spark_client_command
     + 'hdfs dfs -mkdir -p /tpc-ds-files/pre_generated_queries && hdfs dfs -copyFromLocal /tpc-ds-files/pre_generated_queries /tpc-ds-files/')
    log("- wait for copy_queries")
    copy_queries.wait()
    log("+ copy_queries retured with exitcode={}".format(copy_queries.returncode))

def setup_history_server():
    p = popen_str(spark_client_command
     + 'setup-history-server.sh')
    log("- wait for setup-history-server")
    p.wait()
    log("+ setup-history-server retured with exitcode={}".format(p.returncode))

def create_parquet_files(scale):
    p = popen_str(spark_client_command
     + 'hdfs dfs -mkdir -p /tpc-ds-files/data/parquet_{scale} && spark-sql --master yarn --deploy-mode client -f /tpc-ds-files/ddl/tpcds_{scale}.sql'.format(scale=scale))
    log("- wait for create_parquet_files({})".format(scale))
    p.wait()
    log("+ create_parquet_files({}) retured with exitcode={}".format(scale, p.returncode))

# def run_benchmarks(scales):
#     wait_list = []
#
#     for scale in scales:
#         run = popen_str(spark_client_command
#          + 'spark-submit --master yarn --deploy-mode cluster /root/scripts/query.py -s {scale} -hf /tpc-ds-files/pre_generated_queries/query52.sql --name query52_cluster_{scale}G'.format(scale))
#
#         wait_list.append(("run {}".format(scale), run))
#
#     for msg, process in wait_list:
#         print("- wait for {msg}".format(msg=msg))
#         process.wait()
#         print("+ {msg} returned with exitcode={exitcode}".format(msg=msg, exitcode=process.returncode))

def run_benchmark(scale):
    run = popen_str(spark_client_command
     + 'spark-submit --master yarn --deploy-mode cluster /root/scripts/query.py -s {scale} -hf /tpc-ds-files/pre_generated_queries/query52.sql --name query52_cluster_{scale}G'.format(scale=scale))

    log("- wait for run_benchmark({})".format(scale))
    run.wait()
    log("+ run_benchmark({scale}) returned with exitcode={exitcode}".format(scale=scale, exitcode=run.returncode))


def main():
    scales = sys.argv[1:]

    print_time() # log time
    run_the_cluster()
    print_time() # log time
    generate_tpc_ds_for_scales(scales)
    print_time() # log time
    copy_to_hdfs()
    print_time() # log time
    setup_history_server()
    for scale in scales:
        print_time() # log time
        create_parquet_files(scale)
    for scale in scales:
        print_time() # log time
        run_benchmark(scale)
    print_time() # log time


if __name__ == "__main__":
    main()
