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
OPTIONS(header "false", delimiter "|", path "{data_path}/{table_name}.dat")
;
drop table if exists {table_name};
create table {table_name}
using parquet
as (select * from {table_name}_text)
;
drop table if exists {table_name}_text;

"""
data_path = os.environ['data_path']

with open(out_file_path, 'w') as out_file, open(in_file_path, 'r', encoding='utf-8') as in_file:
    matches = re.finditer(regex, in_file.read(), re.MULTILINE)

    for match in matches:
        groups = list(match.groups())
        out_file.write(template.format(data_path=data_path, table_name=groups[0], table_columns=groups[1]))

    # for matchNum, match in enumerate(matches, start=1):
    #     print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
    #
    #     for groupNum in range(0, len(match.groups())):
    #         groupNum = groupNum + 1
    #
    #         print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
