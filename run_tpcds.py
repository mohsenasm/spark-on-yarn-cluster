#!/usr/bin/python3

import subprocess
import sys
import datetime
import pathlib
import os
import threading

def log(msg):
    print(str(msg) + "\r", flush=True)
    with open("output/stdout.txt","a") as f:
        f.write(str(msg) + "\n")
    with open("output/runner_log.txt","a") as f:
        f.write(str(msg) + "\n")
    with open("output/stderr.txt","a") as f:
        f.write(str(msg) + "\n")

def print_time():
    log("T " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

def popen(command):
    with open("output/stdout.txt","ab") as out, open("output/stderr.txt","ab") as err:
        log("C run command: " + str(command))
        return subprocess.Popen(command, stdout=out, stderr=err)

def popen_str(command_str):
    command = command_str.split()
    return popen(command)

def popen_nohup_str(command_str):
    command_str = "nohup " + command_str
    command = command_str.split()
    return popen(command)

def run_the_cluster():
    i = 1
    for command in run_cluster_commmands:
        up = popen_nohup_str(command)
        log(f"- run_the_cluster.({i}/{len(run_cluster_commmands)})({command}) wating ...")
        up.wait()
        log("+ run_the_cluster returned with exitcode => {}".format(up.returncode))
        i += 1

def generate_tpc_ds_for_scales(scales):
    wait_list = []

    copy_queries = popen_nohup_str(f"docker-compose -f {docker_compose_file_name} run tpc-ds /run.sh copy_queries")
    wait_list.append(("copy_queries", copy_queries))

    for scale in scales:
        gen_data = popen_nohup_str(f"docker-compose -f {docker_compose_file_name} run tpc-ds /run.sh gen_data {scale}")
        wait_list.append(("gen_data({})".format(scale), gen_data))

        if use_csv_instead_of_parquet:
            gen_ddl_csv = popen_nohup_str(f"docker-compose -f {docker_compose_file_name} run tpc-ds /run.sh gen_ddl_csv {scale}")
            wait_list.append(("gen_ddl_csv({})".format(scale), gen_ddl_csv))
        else:
            gen_ddl = popen_nohup_str(f"docker-compose -f {docker_compose_file_name} run tpc-ds /run.sh gen_ddl {scale}")
            wait_list.append(("gen_ddl({})".format(scale), gen_ddl))

    for msg, process in wait_list:
        log("- {msg} wating ...".format(msg=msg))
        process.wait()
        log("+ {msg} returned with exitcode => {exitcode}".format(msg=msg, exitcode=process.returncode))

def copy_to_hdfs(scales):
    spark_client_command = get_spark_client_command()

    for scale in scales:
        mkdir = popen_nohup_str(spark_client_command
         + 'hdfs dfs -mkdir -p /tpc-ds-files/data')
        log("- copy_data_to_hdfs({}).mkdir wating ...".format(scale))
        mkdir.wait()
        log("+ copy_data_to_hdfs({}).mkdir retured with exitcode => {}".format(scale, mkdir.returncode))

        copy_data = popen_nohup_str(spark_client_command
         + 'hdfs dfs -copyFromLocal /tpc-ds-files/data/csv_{scale} /tpc-ds-files/data/csv_{scale}'.format(scale=scale))
        log("- copy_data_to_hdfs({}) wating ...".format(scale))
        copy_data.wait()
        log("+ copy_data_to_hdfs({}) retured with exitcode => {}".format(scale, copy_data.returncode))

    mkdir = popen_nohup_str(spark_client_command
     + 'hdfs dfs -mkdir -p /tpc-ds-files/pre_generated_queries')
    log("- copy_queries_to_hdfs.mkdir wating ...")
    mkdir.wait()
    log("+ copy_queries_to_hdfs.mkdir retured with exitcode => {}".format(mkdir.returncode))

    copy_queries = popen_nohup_str(spark_client_command
     + 'hdfs dfs -copyFromLocal /tpc-ds-files/pre_generated_queries /tpc-ds-files/')
    log("- copy_queries_to_hdfs wating ...")
    copy_queries.wait()
    log("+ copy_queries_to_hdfs retured with exitcode => {}".format(copy_queries.returncode))

def remove_csv_data_from_local(scales):
    for scale in scales:
        rm = popen_nohup_str(f'docker-compose -f {docker_compose_file_name} run tpc-ds '
         + 'rm -r /tpc-ds-files/data/csv_{scale}'.format(scale=scale))
        log("- remove_csv_data_from_local({}) wating ...".format(scale))
        rm.wait()
        log("+ remove_csv_data_from_local({}) retured with exitcode => {}".format(scale, rm.returncode))

def setup_history_server():
    spark_client_command = get_spark_client_command()

    p = popen_nohup_str(spark_client_command
     + 'setup-history-server.sh')
    log("- setup-history-server wating ...")
    p.wait()
    log("+ setup-history-server retured with exitcode => {}".format(p.returncode))

def create_tables(scale):
    spark_client_command = get_spark_client_command()

    use_csv_postfix = "_csv" if use_csv_instead_of_parquet else ""

    check_exist = popen_nohup_str(spark_client_command
     + 'hdfs dfs -mkdir /tpc-ds-files/data/parquet_{scale}'.format(scale=scale)).wait()
    if str(check_exist) == "0":
        mkdir = popen_nohup_str(spark_client_command
         + 'hdfs dfs -mkdir -p /tpc-ds-files/data/parquet_{scale}'.format(scale=scale))
        log("- create_tables({}).mkdir_parquet wating ...".format(scale))
        mkdir.wait()
        log("+ create_tables({}).mkdir_parquet retured with exitcode => {}".format(scale, mkdir.returncode))

        parquet = popen_nohup_str(spark_client_command
         + '/opt/spark/bin/spark-sql --master yarn --deploy-mode client -f /tpc-ds-files/ddl/tpcds_{scale}{use_csv_postfix}.sql --name create_db_scale_{scale} --queue {create_tables_queue} {additional_spark_config}'.format(scale=scale, use_csv_postfix=use_csv_postfix, create_tables_queue=create_tables_queue, additional_spark_config=additional_spark_config))
        log("- create_tables({}) wating ...".format(scale))
        parquet.wait()
        log("+ create_tables({}) retured with exitcode => {}".format(scale, parquet.returncode))
    else:
        log("+ create_tables({}) skipped".format(scale))

def remove_parquet_files(scale):
    spark_client_command = get_spark_client_command()

    rm = popen_nohup_str(spark_client_command
     + 'hdfs dfs -rm -r /tpc-ds-files/data/parquet_{scale}'.format(scale=scale))
    log("- remove_parquet_files({}) wating ...".format(scale))
    rm.wait()
    log("+ remove_parquet_files({}) retured with exitcode => {}".format(scale, rm.returncode))

def remove_csv_data_from_hdfs(scales):
    spark_client_command = get_spark_client_command()

    for scale in scales:
        rm = popen_nohup_str(spark_client_command
         + 'hdfs dfs -rm -r /tpc-ds-files/data/csv_{scale}'.format(scale=scale))
        log("- remove_csv_data_from_hdfs({}) wating ...".format(scale))
        rm.wait()
        log("+ remove_csv_data_from_hdfs({}) retured with exitcode => {}".format(scale, rm.returncode))

def run_benchmark(query, scale, queue="default"):
    spark_client_command = get_spark_client_command()
    use_csv_postfix = "_csv" if use_csv_instead_of_parquet else ""

    if run_benchmarks_with_spark_sql:
        cmd = '/opt/spark/bin/spark-sql --master yarn --deploy-mode client --queue {queue} --conf spark.sql.crossJoin.enabled=true -database scale_{scale}{use_csv_postfix} -f /tpc-ds-files/pre_generated_queries/query{query}.sql --name query{query}_cluster_{scale}G {additional_spark_config}'
    else:
        cmd = '/opt/spark/bin/spark-submit --master yarn --deploy-mode client --queue {queue} {additional_spark_config} /root/scripts/query.py -s {scale} -hf /tpc-ds-files/pre_generated_queries/query{query}.sql --name query{query}_cluster_{scale}G'

    for run_id in range(run_count):
        query_log_info = "({}, {}, {})[{}/{}]".format(query, scale, queue, run_id+1, run_count)

        run = popen_nohup_str(spark_client_command
         + cmd.format(queue=queue, query=query, scale=scale, additional_spark_config=additional_spark_config, use_csv_postfix=use_csv_postfix))

        log("- run_benchmark{query_log_info} wating ...".format(query_log_info=query_log_info))
        try:
            run.wait(timeout=60*run_benchmark_timeout) # timeout in seconds
            log("+ run_benchmark{query_log_info} returned with exitcode => {exitcode}".format(query_log_info=query_log_info, exitcode=run.returncode))
        except subprocess.TimeoutExpired:
            log("+ run_benchmark{query_log_info} does not terminate after {timeout} min, terminating ...".format(query_log_info=query_log_info, timeout=run_benchmark_timeout))
            run.terminate()
            log("+ run_benchmark{query_log_info} terminated".format(query_log_info=query_log_info))

def copy_history():
    spark_client_command = get_spark_client_command()

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

    copy_to_host = popen_nohup_str("docker cp {}:/spark-history ./output".format(container_id))
    log("- copy_history wating ...")
    copy_to_host.wait()
    log("+ copy_history returned with exitcode => {exitcode}".format(exitcode=copy_to_host.returncode))

run_benchmark_timeout = 45 # minutes

def run_all_scales():
    pathlib.Path('output').mkdir(parents=True, exist_ok=False)

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
        create_tables(scale); print_time() # log time
    remove_csv_data_from_hdfs(scales); print_time() # log time
    for scale in scales:
        for query in queries:
            run_benchmark(query, scale); print_time() # log time
    copy_history(); print_time() # log time

def run_all_scales_one_by_one():
    pathlib.Path('output').mkdir(parents=True, exist_ok=False)

    scales = sys.argv[1:]

    queries = [5, 19, 21, 26, 40, 52]
    if run_all_queries:
        additional_queries = [i for i in range(1, 100) if i not in queries]
        queries = queries + additional_queries

    # convert 1 to '01', 2 to '02', ...
    queries = [q_name if len(q_name)==2 else "0"+q_name for q_name in map(str, queries)]

    print_time() # log time
    run_the_cluster(); print_time() # log time

    for scale in scales:
        generate_tpc_ds_for_scales([scale]); print_time() # log time
        copy_to_hdfs([scale]); print_time() # log time
        remove_csv_data_from_local([scale]); print_time() # log time
        setup_history_server(); print_time() # log time
        create_tables(scale); print_time() # log time
        if not use_csv_instead_of_parquet:
            remove_csv_data_from_hdfs([scale]); print_time() # log time
        for query in queries:
            threads = []
            for queue in queue_names:
                threads.append(threading.Thread(target=run_benchmark, kwargs={"query": query, "scale": scale, "queue": queue}))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            print_time() # log time
        copy_history(); print_time() # log time
        if use_csv_instead_of_parquet:
            remove_csv_data_from_hdfs([scale]); print_time() # log time
        else:
            remove_parquet_files(scale); print_time() # log time


docker_compose_file_name = "spark-client-with-tpcds-docker-compose.yml"
run_cluster_commmands = ["docker-compose -f spark-client-with-tpcds-docker-compose.yml up -d"]
run_benchmarks_with_spark_sql = (os.getenv("BNCH_SPARK_SQL", "TRUE").upper() == "TRUE")
run_all_queries = (os.getenv("RUN_ALL_QUERIES", "False").upper() == "TRUE")
additional_spark_config = os.getenv("ADDITIONAL_SPARK_CONFIG", "")
use_csv_instead_of_parquet = (os.getenv("USE_CSV", "False").upper() == "TRUE") and run_benchmarks_with_spark_sql
create_tables_queue = os.getenv("CREATE_TABLE_QUEUE", "default")
run_count = int(os.getenv("RUN_COUNT", "1"))
queue_names = set(os.getenv("QUEUE_NAMES", "default").split(','))

def get_spark_client_command():
    return f"docker-compose -f {docker_compose_file_name} run spark-client "

if __name__ == "__main__":
    run_all_scales_one_by_one()

# run sample:
# ADDITIONAL_SPARK_CONFIG='--num-executors 15 --executor-cores 2 --executor-memory 2G' BNCH_SPARK_SQL=false RUN_COUNT='3' QUEUE_NAMES='alpha,beta' CREATE_TABLE_QUEUE='alpha' python3 run_tpcds.py 1 2
