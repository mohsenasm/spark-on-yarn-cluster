#!/bin/bash

case "$1" in
  "bash")
    bash
    ;;
  "exit")
    exit 0
    ;;
  "gen_data")
    mkdir -p /tpc-ds-files/data && cd tools && ./dsdgen -SCALE ${2:-1} -DIR /tpc-ds-files/data
    ;;
  "gen_queries")
    mkdir -p /tpc-ds-files/query && cd tools && ./dsqgen -DIRECTORY ../query_templates -INPUT ../query_templates/templates.lst -SCALE ${2:-1} -VERBOSE Y -QUALIFY Y -OUTPUT_DIR /tpc-ds-files/query
    ;;
  *)
    echo "args parsing error."
    exit 1
    ;;
esac
