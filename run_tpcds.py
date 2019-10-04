#!/usr/bin/python3

import subprocess
import sys
import datetime
import pathlib

def log(msg):
    print(str(msg) + "\r", flush=True)
    with open("output/stdout.txt","a") as out:
        out.write(str(msg) + "\n")
    with open("output/runner_log.txt","a") as out:
        out.write(str(msg) + "\n")

def print_time():
    log(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def popen(command):
    with open("output/stdout.txt","ab") as out, open("output/stderr.txt","ab") as err:
        # log(command)
        return subprocess.Popen(command, stdout=out, stderr=err)

def popen_str(command_str):
    command = command_str.split()
    return popen(command)

def popen_nohup_str(command_str):
    command_str = "nohup " + command_str
    command = command_str.split()
    return popen(command)

docker_compose_file_name = "spark-client-with-tpcds-docker-compose.yml"
run_cluster_commmand = "docker-compose -f spark-client-with-tpcds-docker-compose.yml up -d --build"

def run_the_cluster():
    up = popen_nohup_str(run_cluster_commmand)
    log(f"- run_the_cluster({run_cluster_commmand}) wating ...")
    up.wait()
    log("+ run_the_cluster returned with exitcode => {}".format(up.returncode))

def generate_tpc_ds_for_scales(scales):
    wait_list = []

    copy_queries = popen_nohup_str(f"docker-compose -f {docker_compose_file_name} run tpc-ds /run.sh copy_queries")
    wait_list.append(("copy_queries", copy_queries))

    for scale in scales:
        gen_data = popen_nohup_str(f"docker-compose -f {docker_compose_file_name} run tpc-ds /run.sh gen_data {scale}")
        gen_ddl = popen_nohup_str(f"docker-compose -f {docker_compose_file_name} run tpc-ds /run.sh gen_ddl {scale}")

        wait_list.append(("gen_data {}".format(scale), gen_data))
        wait_list.append(("gen_ddl {}".format(scale), gen_ddl))

    for msg, process in wait_list:
        log("- {msg} wating ...".format(msg=msg))
        process.wait()
        log("+ {msg} returned with exitcode => {exitcode}".format(msg=msg, exitcode=process.returncode))

spark_client_command = f"docker-compose -f {docker_compose_file_name} run spark-client "

def copy_to_hdfs(scales):
    for scale in scales:
        mkdir = popen_nohup_str(spark_client_command
         + 'hdfs dfs -mkdir -p /tpc-ds-files/data')
        log("- copy_data({}).mkdir wating ...".format(scale))
        mkdir.wait()
        log("+ copy_data({}).mkdir retured with exitcode => {}".format(scale, mkdir.returncode))

        copy_data = popen_nohup_str(spark_client_command
         + 'hdfs dfs -copyFromLocal /tpc-ds-files/data/csv_{scale} /tpc-ds-files/data/csv_{scale}'.format(scale=scale))
        log("- copy_data({}) wating ...".format(scale))
        copy_data.wait()
        log("+ copy_data({}) retured with exitcode => {}".format(scale, copy_data.returncode))

    mkdir = popen_nohup_str(spark_client_command
     + 'hdfs dfs -mkdir -p /tpc-ds-files/pre_generated_queries')
    log("- copy_queries.mkdir wating ...")
    mkdir.wait()
    log("+ copy_queries.mkdir retured with exitcode => {}".format(mkdir.returncode))

    copy_queries = popen_nohup_str(spark_client_command
     + 'hdfs dfs -copyFromLocal /tpc-ds-files/pre_generated_queries /tpc-ds-files/')
    log("- copy_queries wating ...")
    copy_queries.wait()
    log("+ copy_queries retured with exitcode => {}".format(copy_queries.returncode))

def remove_csv_data_from_local(scales):
    for scale in scales:
        rm = popen_nohup_str(f'docker-compose -f {docker_compose_file_name} run tpc-ds '
         + 'rm -r /tpc-ds-files/data/csv_{scale}'.format(scale=scale))
        log("- remove_csv_data_from_local({}) wating ...".format(scale))
        rm.wait()
        log("+ remove_csv_data_from_local({}) retured with exitcode => {}".format(scale, rm.returncode))

def setup_history_server():
    p = popen_nohup_str(spark_client_command
     + 'setup-history-server.sh')
    log("- setup-history-server wating ...")
    p.wait()
    log("+ setup-history-server retured with exitcode => {}".format(p.returncode))

def create_parquet_files(scale):
    check_exist = popen_nohup_str(spark_client_command
     + 'hdfs dfs -mkdir /tpc-ds-files/data/parquet_{scale}'.format(scale=scale)).wait()
    if str(check_exist) == "0":
        mkdir = popen_nohup_str(spark_client_command
         + 'hdfs dfs -mkdir -p /tpc-ds-files/data/parquet_{scale}'.format(scale=scale))
        log("- create_parquet_files({}).mkdir wating ...".format(scale))
        mkdir.wait()
        log("+ create_parquet_files({}).mkdir retured with exitcode => {}".format(scale, mkdir.returncode))

        parquet = popen_nohup_str(spark_client_command
         + '/opt/spark/bin/spark-sql --master yarn --deploy-mode client -f /tpc-ds-files/ddl/tpcds_{scale}.sql'.format(scale=scale))
        log("- create_parquet_files({}) wating ...".format(scale))
        parquet.wait()
        log("+ create_parquet_files({}) retured with exitcode => {}".format(scale, parquet.returncode))
    else:
        log("+ create_parquet_files({}) skipped".format(scale))

def remove_parquet_files(scale):
    rm = popen_nohup_str(spark_client_command
     + 'hdfs dfs -rm -r /tpc-ds-files/data/parquet_{scale}'.format(scale=scale))
    log("- remove_parquet_files({}) wating ...".format(scale))
    rm.wait()
    log("+ remove_parquet_files({}) retured with exitcode => {}".format(scale, rm.returncode))

def remove_csv_data_from_hdfs(scales):
    for scale in scales:
        rm = popen_nohup_str(spark_client_command
         + 'hdfs dfs -rm -r /tpc-ds-files/data/csv_{scale}'.format(scale=scale))
        log("- remove_csv_data_from_hdfs({}) wating ...".format(scale))
        rm.wait()
        log("+ remove_csv_data_from_hdfs({}) retured with exitcode => {}".format(scale, rm.returncode))

def run_benchmark(query, scale):
    run = popen_nohup_str(spark_client_command
     + '/opt/spark/bin/spark-submit --master yarn --deploy-mode client /root/scripts/query.py -s {scale} -hf /tpc-ds-files/pre_generated_queries/query{query}.sql --name query{query}_cluster_{scale}G'.format(query=query, scale=scale))

    log("- run_benchmark({}, {}) wating ...".format(query, scale))
    try:
        run.wait(timeout=60*run_benchmark_timeout) # timeout in seconds
        log("+ run_benchmark({query}, {scale}) returned with exitcode => {exitcode}".format(query=query, scale=scale, exitcode=run.returncode))
    except subprocess.TimeoutExpired:
        log("+ run_benchmark({query}, {scale}) does not terminate after {timeout} min, terminating ...".format(query=query, scale=scale, timeout=run_benchmark_timeout))
        run.terminate()
        log("+ run_benchmark({query}, {scale}) terminated".format(query=query, scale=scale))


def copy_history():
    rm_old_logs = popen_nohup_str(spark_client_command
     + 'rm /spark-history/*')
    log("- copy_history.rm_old_logs wating ...")
    rm_old_logs.wait()
    log("+ copy_history.rm_old_logs returned with exitcode => {exitcode}".format(exitcode=rm_old_logs.returncode))

    copy_to_container = popen_nohup_str(spark_client_command
     + 'hdfs dfs -copyToLocal /spark-history/* /spark-history/')
    log("- copy_history.to_container wating ...")
    copy_to_container.wait()
    log("+ copy_history.to_container returned with exitcode => {exitcode}".format(exitcode=copy_to_container.returncode))

    container_id = subprocess.check_output(f"docker-compose -f {docker_compose_file_name} ps -q spark-client".split()).decode("utf-8").strip()

    copy_to_host = popen_nohup_str("docker cp {}:/spark-history .".format(container_id))
    log("- copy_history wating ...")
    copy_to_host.wait()
    log("+ copy_history returned with exitcode => {exitcode}".format(exitcode=copy_to_host.returncode))

run_benchmark_timeout = 5 # minutes

def run_all_scales():
    pathlib.Path('output').mkdir(parents=True, exist_ok=True)

    scales = sys.argv[1:]
    queries = [5, 19, 21, 26, 40, 52]
    # queries = [19, 21, 26, 40, 52]

    print_time() # log time
    run_the_cluster(); print_time() # log time
    generate_tpc_ds_for_scales(scales); print_time() # log time
    copy_to_hdfs(scales); print_time() # log time
    remove_csv_data_from_local(scales); print_time() # log time
    setup_history_server(); print_time() # log time
    for scale in scales:
        create_parquet_files(scale); print_time() # log time
    remove_csv_data_from_hdfs(scales); print_time() # log time
    for scale in scales:
        for query in queries:
            run_benchmark(query, scale); print_time() # log time
    copy_history(); print_time() # log time

def run_all_scales_one_by_one():
    pathlib.Path('output').mkdir(parents=True, exist_ok=True)

    scales = sys.argv[1:]
    queries = [5, 19, 21, 26, 40, 52]
    # queries = [19, 21, 26, 40, 52]

    print_time() # log time
    for scale in scales:
        run_the_cluster(); print_time() # log time
        generate_tpc_ds_for_scales([scale]); print_time() # log time
        copy_to_hdfs([scale]); print_time() # log time
        remove_csv_data_from_local([scale]); print_time() # log time
        setup_history_server(); print_time() # log time
        create_parquet_files(scale); print_time() # log time
        remove_csv_data_from_hdfs([scale]); print_time() # log time
        for query in queries:
            run_benchmark(query, scale); print_time() # log time
        copy_history(); print_time() # log time
        remove_parquet_files(scale); print_time() # log time

if __name__ == "__main__":
    run_all_scales_one_by_one()
