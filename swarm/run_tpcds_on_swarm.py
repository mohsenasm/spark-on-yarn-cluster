import sys
sys.path.append("..")
import run_tpcds

if __name__ == "__main__":
    run_tpcds.docker_compose_file_name = "spark-swarm-client.yml"
    run_tpcds.run_cluster_commmands = \
        ["docker-compose -f spark-swarm-client.yml up -d"]

    run_tpcds.run_all_scales_one_by_one()
