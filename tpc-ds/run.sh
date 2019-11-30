#!/bin/bash

case "$1" in
  "bash")
    bash
    ;;
  "exit")
    exit 0
    ;;
  "gen_data")
    mkdir -p /tpc-ds-files/data/csv_${2:-1} && cd /tpcds-kit/tools && ./dsdgen -SCALE ${2:-1} -DIR /tpc-ds-files/data/csv_${2:-1}
    ;;
  "rm_data")
    rm -r /tpc-ds-files/data/csv
    ;;
  # "gen_queries")
  #   mkdir -p /tpc-ds-files/query && cd /tpcds-kit/tools && ./dsqgen -DIRECTORY ../query_templates -INPUT ../query_templates/templates.lst -SCALE ${2:-1} -VERBOSE Y -QUALIFY Y -OUTPUT_DIR /tpc-ds-files/query
  #   ;;
  "copy_queries")
    mkdir -p /tpc-ds-files/pre_generated_queries && cp -r /pre_generated_queries/* /tpc-ds-files/pre_generated_queries/
    ;;
  "gen_ddl")
    mkdir -p /tpc-ds-files/ddl && cd /tpcds-kit/tools && python3 /opt/gen_ddl.py ${2:-1} tpcds.sql /tpc-ds-files/ddl/tpcds_${2:-1}.sql
    ;;
  "gen_ddl_csv")
    mkdir -p /tpc-ds-files/ddl && cd /tpcds-kit/tools && python3 /opt/gen_ddl_csv.py ${2:-1} tpcds.sql /tpc-ds-files/ddl/tpcds_${2:-1}_csv.sql
    ;;
  *)
    echo "args parsing error."
    exit 1
    ;;
esac
