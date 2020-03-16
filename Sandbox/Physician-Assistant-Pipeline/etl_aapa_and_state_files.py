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
from collections import namedtuple

glue_context = GlueContext(SparkContext.getOrCreate())

AAPAFiles = namedtuple('AAPAFiles', 'master_file_df license_df paprograms_education_df primary_speciality_df')
StateFiles = namedtuple('StateFiles', 'tn_df co_df')

'''
def load_aapa_files():
    master_file = glue_context.create_dynamic_frame.from_catalog(database="pa_data_crawler_output",
                                                                 table_name="master_csv")
    # dynamic frames do not suport left join so convert to spark dataframes
    aapa_files.master_file_df = master_file.toDF()

    license = glue_context.create_dynamic_frame.from_catalog(database="pa_data_crawler_output",
                                                             table_name="license_csv")
    aapa_files.license_df = license.toDF()

    paprograms = glue_context.create_dynamic_frame.from_catalog(database="pa_data_crawler_output",
                                                                table_name="paprograms_csv")
    aapa_files.paprograms_education_df = paprograms.toDF()

    primary_speciality = glue_context.create_dynamic_frame.from_catalog(database="pa_data_crawler_output",
                                                                        table_name="primary_csv")
    aapa_files.primary_speciality_df = primary_speciality.toDF()

    return (aapa_files)


def load_state_files():
    tn = glue_context.create_dynamic_frame.from_catalog(database="pa_data_crawler_output", table_name="tn_pa_list_csv")
    state_files.tn_df = tn.toDF()

    co = glue_context.create_dynamic_frame.from_catalog(database="pa_data_crawler_output", table_name="co_pa_list_csv")
    state_files.co_df = co.toDF()

    return (state_files)
'''

def load_aapa_files():
    master_file = glue_context.create_dynamic_frame.from_catalog(database="pa_data_crawler_output",
                                                                 table_name="master_csv")
    # dynamic frames do not suport left join so convert to spark dataframes
    license = glue_context.create_dynamic_frame.from_catalog(database="pa_data_crawler_output",
                                                             table_name="license_csv")

    paprograms = glue_context.create_dynamic_frame.from_catalog(database="pa_data_crawler_output",
                                                                table_name="paprograms_csv")

    primary_speciality = glue_context.create_dynamic_frame.from_catalog(database="pa_data_crawler_output",
                                                                        table_name="primary_csv")
    return AAPAFiles(
        master_file_df=master_file.toDF(),
        license_df=license.toDF(),
        paprograms_education_df=paprograms.toDF(),
        primary_speciality_df=primary_speciality.toDF()
    )

def load_state_files():
    tn = glue_context.create_dynamic_frame.from_catalog(database="pa_data_crawler_output", table_name="tn_pa_list_csv")
    tn_df = tn.toDF()

    co = glue_context.create_dynamic_frame.from_catalog(database="pa_data_crawler_output", table_name="co_pa_list_csv")
    co_df = co.toDF()

    return StateFiles(
        tn_df = tn.toDF(),
        co_df=co.toDF()
    )

def aapa_pre_processing(aapa_files):
    license_df = aapa_files.license_df.withColumnRenamed("id", "idx")
    paprograms_education_df = aapa_files.paprograms_education_df.withColumnRenamed("id", "idy")
    primary_speciality_df = aapa_files.primary_speciality_df.withColumnRenamed("id", "idz")

    return AAPAFiles(
        master_file_df=aapa_files.master_file_df,
        license_df=license_df,
        paprograms_education_df=paprograms_education_df,
        primary_speciality_df=primary_speciality_df
    )


def join_aapa_files(aapa_files):
    master_license_joined = aapa_files.master_file_df.join(aapa_files.license_df,
                                                           aapa_files.master_file_df.id == aapa_files.license_df.idx,
                                                           'outer')
    master_license_programs_joined = master_license_joined.join(aapa_files.paprograms_education_df,
                                                                master_license_joined.prog == aapa_files.paprograms_education_df.idy,
                                                                'left')
    master_license_programs_speciality_joined = master_license_programs_joined.join(aapa_files.primary_speciality_df,
                                                                                    master_license_programs_joined.spec == aapa_files.primary_speciality_df.idz,
                                                                                    'left')

    return (master_license_programs_speciality_joined)


def joined_aapa_files_transformation(master_license_programs_speciality_joined):
    master_license_programs_speciality_joined = master_license_programs_speciality_joined.drop('fill1', 'fill2', 'idx',
                                                                                               'idy', 'idz', 'prog',
                                                                                               'spec')
    master_license_programs_speciality_joined = master_license_programs_speciality_joined.withColumnRenamed("Name",
                                                                                                            "spec")
    master_license_programs_speciality_joined = master_license_programs_speciality_joined.withColumnRenamed(
        "PA Program Name", "prog")

    return (master_license_programs_speciality_joined)


def state_pre_processing(state_files):
    tn_df = state_files.tn_df.select(
        'FirstName', 'MiddleName', 'LastName', 'Title', 'PracticeName', 'PracticeAddress', 'PracticeAddress2', \
        'PracticeCity', 'PracticeState', 'PracticeZIP', 'EducationProvider', 'ExpirationDate', 'LicenseNumber'
    ) \
        .withColumnRenamed('FirstName', 'fname') \
        .withColumnRenamed('MiddleName', 'mname') \
        .withColumnRenamed('LastName', 'lname') \
        .withColumnRenamed('Title', 'suffix') \
        .withColumnRenamed('LicenseNumber', 'license') \
        .withColumnRenamed('ExpirationDate', 'expires') \
        .withColumnRenamed('PracticeName', 'company') \
        .withColumnRenamed('PracticeAddress', 'wal1') \
        .withColumnRenamed('PracticeAddress2', 'wal2') \
        .withColumnRenamed('PracticeCity', 'wcity') \
        .withColumnRenamed('PracticeState', 'wstate') \
        .withColumnRenamed('PracticeZIP', 'wzip') \
        .withColumnRenamed('EducationProvider', 'prog')

    co_df = state_files.co_df.select(
        'First Name', 'Middle Name', 'Last Name', 'Suffix', 'Attention', 'Address Line 1', \
        'Address Line 2', 'City', 'State', 'Mail Zip Code', 'Specialty', 'License Expiration Date', \
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

    return StateFiles(
        tn_df = tn_df,
        co_df=co_df
    )


def merge_all_files(master_license_programs_speciality_joined, state_files):
    dfs = [master_license_programs_speciality_joined, state_files.co_df, state_files.tn_df]

    def merge_column_data(dfs):
        columns = reduce(lambda x, y: set(x).union(set(y)), [i.columns for i in dfs])
        for i in range(len(dfs)):
            d = dfs[i]
            for c in columns:
                if c not in d.columns:
                    d = d.withColumn(c, lit(None))
            dfs[i] = d

        return stitch_columns(dfs)

    def stitch_columns(dfs):
        return reduce(lambda df1, df2: df1.union(df2.select(df1.columns)), dfs)

    merged_df = merge_column_data(dfs)

    return (merged_df)


def transform_merged_file_for_matching(merged_df):
    df_added_pkey = merged_df.select("*").withColumn("pkey", monotonically_increasing_id())

    '''
    from pyspark.sql.functions import *
    newDf = df_transformed.withColumn('Name', regexp_replace('Name', '"', ''))
    '''

    df_changed_datatype = df_added_pkey.select([col(c).cast("string") for c in df_added_pkey.columns])

    column_names = df_changed_datatype.columns
    for column in column_names:
        df_transformed = df_changed_datatype.withColumn(column, regexp_replace(column, ",", "."))

    df_transformed.printSchema()
    df_transformed.show(20)
    return (df_transformed)


def write_file_to_s3(df_transformed):
    df_transformed \
        .repartition(1) \
        .write \
        .mode('overwrite') \
        .option('header', True) \
        .option("nullValue", "") \
        .option("quote", "") \
        .csv("s3://pa-data-output-file-csv/merged")


# .replace('', None)
# .option("nullValue", "") \
def main():
    aapa_files = load_aapa_files()

    state_files = load_state_files()

    aapa_files = aapa_pre_processing(aapa_files)

    aapa_joined_file = join_aapa_files(aapa_files)

    aapa_joined_file = joined_aapa_files_transformation(aapa_joined_file)

    state_files = state_pre_processing(state_files)

    merged_file = merge_all_files(aapa_joined_file, state_files)

    final_file = transform_merged_file_for_matching(merged_file)

    write_file_to_s3(final_file)


#if __name__ == "__main__":
main()