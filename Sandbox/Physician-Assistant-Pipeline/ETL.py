import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import udf, monotonically_increasing_id, lit, col
from pyspark.sql.types import StringType
from datetime import datetime
from functools import reduce

glueContext = GlueContext(SparkContext.getOrCreate())

master = glueContext.create_dynamic_frame.from_catalog(database="pa_data_crawler_output", table_name="master_csv")
#dynamic frames do not suport left join so convert to spark dataframes
master_df = master.toDF()

license = glueContext.create_dynamic_frame.from_catalog(database="pa_data_crawler_output", table_name="license_csv")
license_df = license.toDF()

paprograms = glueContext.create_dynamic_frame.from_catalog(database="pa_data_crawler_output", table_name="paprograms_csv")
paprograms_df = paprograms.toDF()

primary = glueContext.create_dynamic_frame.from_catalog(database="pa_data_crawler_output", table_name="primary_csv")
primary_df = primary.toDF()

license_df = license_df.withColumnRenamed("id", "idx")
paprograms_df = paprograms_df.withColumnRenamed("id", "idy")
primary_df = primary_df.withColumnRenamed("id", "idz")

ml = master_df.join(license_df, master_df.id == license_df.idx, 'outer')
mlp = ml.join(paprograms_df, ml.prog == paprograms_df.idy, 'left')
mlpp = mlp.join(primary_df, mlp.spec == primary_df.idz, 'left')


mlpp = mlpp.drop('fill1', 'fill2','idx', 'idy', 'idz' 'prog', 'spec')
mlpp = mlpp.drop('prog')
mlpp= mlpp.withColumnRenamed("Name", "spec")
mlpp = mlpp.withColumnRenamed("PA Program Name", "prog")

tn = glueContext.create_dynamic_frame.from_catalog(database="pa_data_crawler_output", table_name="tn_pa_list_csv")
tn_df = tn.toDF()

co = glueContext.create_dynamic_frame.from_catalog(database="pa_data_crawler_output", table_name="co_pa_list_csv")
co_df = co.toDF()


tn_df = tn_df.select('FirstName','MiddleName','LastName','Title','PracticeName','PracticeAddress','PracticeAddress2', \
'PracticeCity','PracticeState','PracticeZIP','EducationProvider','ExpirationDate','LicenseNumber') \
.withColumnRenamed('FirstName','fname') \
.withColumnRenamed('MiddleName','mname')\
.withColumnRenamed('LastName','lname') \
.withColumnRenamed('Title','suffix')\
.withColumnRenamed('LicenseNumber','license')\
.withColumnRenamed('ExpirationDate','Expires')\
.withColumnRenamed('PracticeName','company')\
.withColumnRenamed('PracticeAddress','wal1')\
.withColumnRenamed('PracticeAddress2','wal2')\
.withColumnRenamed('PracticeCity','wcity')\
.withColumnRenamed('PracticeState','wstate')\
.withColumnRenamed('PracticeZIP','wzip')\
.withColumnRenamed('EducationProvider','prog')


co_df = co_df.select('First Name', 'Middle Name', 'Last Name', 'Suffix', 'Attention', 'Address Line 1', 'Address Line 2', 'City', 'State', 'Mail Zip Code', 'Specialty' ,'License Expiration Date', 'License Number', 'License Type') \
.withColumnRenamed('First Name','fname') \
.withColumnRenamed('Suffix','Suffix') \
.withColumnRenamed('Middle Name','mname') \
.withColumnRenamed('Last Name','lname') \
.withColumnRenamed('Attention','company') \
.withColumnRenamed('Address Line 1','wal1') \
.withColumnRenamed('Address Line 2','wal2') \
.withColumnRenamed('City','wcity') \
.withColumnRenamed('State','wstate') \
.withColumnRenamed('Mail Zip Code','wzip') \
.withColumnRenamed('Specialty','spec') \
.withColumnRenamed('License Expiration Date','expires') \
.withColumnRenamed('License Number','license') \
.withColumnRenamed('License Type','type')

dfs = [mlpp, co_df, tn_df]
def concat(dfs):
    return reduce(lambda df1, df2: df1.union(df2.select(df1.columns)), dfs)
def union_all(dfs):
    columns = reduce(lambda x, y : set(x).union(set(y)), [ i.columns for i in dfs ])
    for i in range(len(dfs)):
        d = dfs[i]
        for c in columns:
            if c not in d.columns:
                d = d.withColumn(c, lit(None))
        dfs[i] = d

    return concat(dfs)
joined = union_all(dfs)

df_transform = joined.select("*").withColumn("pkey", monotonically_increasing_id())

'''
from pyspark.sql.functions import *
newDf = df_transform.withColumn('Name', regexp_replace('Name', '"', ''))
'''

df_transform = df_transform.select([col(c).cast("string") for c in df_transform.columns])

from pyspark.sql.functions import regexp_replace,col


colss = df_transform.columns # list of all columns
for col in colss:
    df_transform = df_transform.withColumn(col, regexp_replace(col, ",", "."))

df_transform.printSchema()
df_transform.show(20)

df_transform \
    .repartition(1)\
    .write \
    .mode('overwrite') \
    .option('header',True) \
    .option("nullValue", "") \
    .option("quote","") \
    .csv("s3://pa-data-output-file-csv/merged")
#.replace('', None)
#.option("nullValue", "") \