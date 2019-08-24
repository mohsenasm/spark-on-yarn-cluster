#!/bin/bash

case "$1" in
  "bash")
    bash
    ;;
  "exit")
    exit 0
    ;;
  "gen_data")
    mkdir -p /tpc-ds-files/data && cd /tpcds-kit/tools && ./dsdgen -SCALE ${2:-1} -DIR /tpc-ds-files/data
    ;;
  "gen_queries")
    mkdir -p /tpc-ds-files/query && cd /tpcds-kit/tools && ./dsqgen -DIRECTORY ../query_templates -INPUT ../query_templates/templates.lst -SCALE ${2:-1} -VERBOSE Y -QUALIFY Y -OUTPUT_DIR /tpc-ds-files/query
    ;;
  "gen_ddl")
    mkdir -p /tpc-ds-files/ddl && cd /tpcds-kit/tools && python3 /opt/gen_ddl.py tpcds.sql /tpc-ds-files/ddl/tpcds.sql
    ;;
  *)
    echo "args parsing error."
    exit 1
    ;;
esac
