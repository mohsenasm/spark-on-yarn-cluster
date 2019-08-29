import re, sys, os

regex = r"create table (\w*)\s*\(([^;]*)\);"
in_file_path = sys.argv[1]
out_file_path = sys.argv[2]
template = """---------------------------------------------
drop table if exists {table_name}_text;
create table {table_name}_text
(
{table_columns}
)
USING csv
OPTIONS(header "false", delimiter "|", path "{data_path}/csv/{table_name}.dat")
;
drop table if exists {table_name};
create table {table_name}
using parquet
OPTIONS(path "{data_path}/parquet/{table_name}")
as (select * from {table_name}_text)
;
drop table if exists {table_name}_text;

"""
data_path = os.environ['data_path']
ignored_tables = ["dbgen_version"]

with open(out_file_path, 'w') as out_file, open(in_file_path, 'r', encoding='utf-8') as in_file:
    matches = re.finditer(regex, in_file.read(), re.MULTILINE)

    for match in matches:
        groups = list(match.groups())

        table_name = groups[0]

        # convert to what HIVE supports.
        table_columns = groups[1].replace("not null", "        ")
        table_columns = re.sub(r',\s*primary key \([^\)]*\)', '', table_columns)

        if table_name not in ignored_tables:
            out_file.write(template.format(data_path=data_path, table_name=table_name, table_columns=table_columns))
