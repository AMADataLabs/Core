import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import udf, monotonically_increasing_id, lit, col, regexp_replace
from pyspark.sql.types import StringType
from datetime import datetime
from functools import reduce

glueContext = GlueContext(SparkContext.getOrCreate())

master_file = glueContext.create_dynamic_frame.from_catalog(database="pa_data_crawler_output", table_name="master_csv")
#dynamic frames do not suport left join so convert to spark dataframes
master_file_df = master_file.toDF()

license = glueContext.create_dynamic_frame.from_catalog(database="pa_data_crawler_output", table_name="license_csv")
license_df = license.toDF()

paprograms = glueContext.create_dynamic_frame.from_catalog(database="pa_data_crawler_output", table_name="paprograms_csv")
paprograms_education_df = paprograms.toDF()

primary_speciality = glueContext.create_dynamic_frame.from_catalog(database="pa_data_crawler_output", table_name="primary_csv")
primary_speciality_df = primary_speciality.toDF()

license_df = license_df.withColumnRenamed("id", "idx")
paprograms_education_df = paprograms_education_df.withColumnRenamed("id", "idy")
primary_speciality_df = primary_speciality_df.withColumnRenamed("id", "idz")

master_license_joined = master_file_df.join(license_df, master_file_df.id == license_df.idx, 'outer')
master_license_programs_joined = master_license_joined.join(paprograms_education_df, master_license_joined.prog == paprograms_education_df.idy, 'left')
master_license_programs_speciality_joined = master_license_programs_joined.join(primary_speciality_df, master_license_programs_joined.spec == primary_speciality_df.idz, 'left')


master_license_programs_speciality_joined = master_license_programs_speciality_joined.drop('fill1', 'fill2', 'idx', 'idy', 'idz', 'prog', 'spec')
master_license_programs_speciality_joined= master_license_programs_speciality_joined.withColumnRenamed("Name", "spec")
master_license_programs_speciality_joined = master_license_programs_speciality_joined.withColumnRenamed("PA Program Name", "prog")

tn = glueContext.create_dynamic_frame.from_catalog(database="pa_data_crawler_output", table_name="tn_pa_list_csv")
tn_df = tn.toDF()

co = glueContext.create_dynamic_frame.from_catalog(database="pa_data_crawler_output", table_name="co_pa_list_csv")
co_df = co.toDF()

tn_df = tn_df.select(
    'FirstName', 'MiddleName', 'LastName', 'Title', 'PracticeName', 'PracticeAddress', 'PracticeAddress2', \
    'PracticeCity', 'PracticeState', 'PracticeZIP', 'EducationProvider', 'ExpirationDate', 'LicenseNumber'
) \
.withColumnRenamed('FirstName', 'fname') \
.withColumnRenamed('MiddleName', 'mname')\
.withColumnRenamed('LastName', 'lname') \
.withColumnRenamed('Title', 'suffix')\
.withColumnRenamed('LicenseNumber', 'license')\
.withColumnRenamed('ExpirationDate', 'expires')\
.withColumnRenamed('PracticeName', 'company')\
.withColumnRenamed('PracticeAddress', 'wal1')\
.withColumnRenamed('PracticeAddress2', 'wal2')\
.withColumnRenamed('PracticeCity', 'wcity')\
.withColumnRenamed('PracticeState', 'wstate')\
.withColumnRenamed('PracticeZIP', 'wzip')\
.withColumnRenamed('EducationProvider', 'prog')

co_df = co_df.select(
    'First Name', 'Middle Name', 'Last Name', 'Suffix', 'Attention', 'Address Line 1', \
    'Address Line 2', 'City', 'State', 'Mail Zip Code', 'Specialty' ,'License Expiration Date', \
    'License Number', 'License Type'
) \
.withColumnRenamed('First Name', 'fname') \
.withColumnRenamed('Suffix', 'Suffix') \
.withColumnRenamed('Middle Name', 'mname') \
.withColumnRenamed('Last Name', 'lname') \
.withColumnRenamed('Attention', 'company') \
.withColumnRenamed('Address Line 1', 'wal1') \
.withColumnRenamed('Address Line 2', 'wal2') \
.withColumnRenamed('City', 'wcity') \
.withColumnRenamed('State', 'wstate') \
.withColumnRenamed('Mail Zip Code', 'wzip') \
.withColumnRenamed('Specialty', 'spec') \
.withColumnRenamed('License Expiration Date', 'expires') \
.withColumnRenamed('License Number', 'license') \
.withColumnRenamed('License Type', 'type')

dfs = [master_license_programs_speciality_joined, co_df, tn_df]

def merge_column_data(dfs):
    columns = reduce(lambda x, y : set(x).union(set(y)), [ i.columns for i in dfs ])
    for i in range(len(dfs)):
        d = dfs[i]
        for c in columns:
            if c not in d.columns:
                d = d.withColumn(c, lit(None))
        dfs[i] = d

    return stitch_columns(dfs)

def stitch_columns(dfs):
    return reduce(lambda df1, df2: df1.union(df2.select(df1.columns)), dfs)

joined_df = merge_column_data(dfs)

df_added_pkey = joined_df.select("*").withColumn("pkey", monotonically_increasing_id())

'''
from pyspark.sql.functions import *
newDf = df_transformed.withColumn('Name', regexp_replace('Name', '"', ''))
'''

df_changed_datatype = df_added_pkey.select([col(c).cast("string") for c in df_added_pkey.columns])

column_names = df_changed_datatype.columns
for col in column_names:
    df_transformed = df_changed_datatype.withColumn(col, regexp_replace(col, ",", "."))

df_transformed.printSchema()
df_transformed.show(20)

df_transformed \
    .repartition(1)\
    .write \
    .mode('overwrite') \
    .option('header', True) \
    .option("nullValue", "") \
    .option("quote", "") \
    .csv("s3://pa-data-output-file-csv/merged")
#.replace('', None)
#.option("nullValue", "") \