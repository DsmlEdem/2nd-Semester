from pyspark.sql import SparkSession
from pprint import pprint

sc = SparkSession \
    .builder \
    .appName("Part 2 Task 1: broadcast join") \
    .getOrCreate() \
    .sparkContext

employees = sc.textFile("files/employeesR.csv") \
        .map(lambda r: r.split(",")) \
        .map(lambda r: (int(r[0]), r[1], int(r[2])))

departments = sc.textFile("files/departmentsR.csv") \
        .map(lambda r: r.split(",")) \
        .map(lambda r: (int(r[0]), r[1]))

employees_tagged = employees.map(lambda r: (r[2], ("emp", r[0], r[1])))
deps_tagged = departments.map(lambda r: (r[0], ("dep", r[1])))

together = employees_tagged.union(deps_tagged)

def make_pairs_from_list(t):
    dep_id = t[0]
    rec_list = t[1]

    emp_list = []
    dep_list = []
    for rec in rec_list:
        if rec[0] == "emp":
            emp_list.append(rec[1:])
        elif rec[0] == "dep":
            dep_list.append(rec[1:])
        else:
            print("This should not happen!")
            assert False

    ret = []
    for emp in emp_list:
        for dep in dep_list:
            ret.append(emp + (dep_id,) + dep)

    return ret

res = together.groupByKey() \
        .flatMap(make_pairs_from_list)

pprint(res.collect())

