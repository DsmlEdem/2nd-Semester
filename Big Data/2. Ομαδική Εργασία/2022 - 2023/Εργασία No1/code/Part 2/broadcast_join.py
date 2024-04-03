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

dep_local_copy = sc.broadcast(departments.keyBy(lambda t: t[0]).collectAsMap())

def fuse_employee_with_its_department(emp):
    emp_id, emp_name, emp_dep_id = emp
    dep_name = dep_local_copy.value[emp_dep_id][1]
    return emp_id, emp_name, emp_dep_id, dep_name

join_result = employees.map(fuse_employee_with_its_department)

pprint(join_result.collect())

