import re, sys, os

regex = r"create table (\w*)\s*\(([^;]*)\);"
scale = sys.argv[1]
in_file_path = sys.argv[2]
out_file_path = sys.argv[3]
template = """---------------------------------------------

drop table if exists {table_name};
create table {table_name}
(
{table_columns}
)
USING csv
OPTIONS(header "false", delimiter "|", path "{data_path}/csv_{scale}/{table_name}.dat")
;

"""
data_path = os.environ['data_path']
ignored_tables = ["dbgen_version"]

template_create_db = """---------------------------------------------

CREATE DATABASE IF NOT EXISTS scale_{scale};
USE scale_{scale}_csv;

"""

with open(out_file_path, 'w') as out_file, open(in_file_path, 'r', encoding='utf-8') as in_file:
    out_file.write(template_create_db.format(scale=scale))

    matches = re.finditer(regex, in_file.read(), re.MULTILINE)

    for match in matches:
        groups = list(match.groups())

        table_name = groups[0]

        # convert to what HIVE supports.
        table_columns = groups[1].replace("not null", "        ")
        table_columns = re.sub(r',\s*primary key \([^\)]*\)', '', table_columns)

        if table_name not in ignored_tables:
            out_file.write(template.format(scale=scale, data_path=data_path, table_name=table_name, table_columns=table_columns))
