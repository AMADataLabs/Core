import pandas as pd
import boto3
import io
client = boto3.client('s3')
resource = boto3.resource('s3')
my_bucket = resource.Bucket('ama-hsg-datalabs-datalake-ingestion-sandbox')

def descriptors_to_csv():
    clinicianDescriptor_obj = client.get_object(Bucket='ama-hsg-datalabs-datalake-ingestion-sandbox', Key='AMA/CPT/20200131/standard/Clinician Descriptors/ClinicianDescriptor.xlsx')
    clinicianDescriptor_file = clinicianDescriptor_obj['Body'].read()
    df_cd = pd.read_excel(io.BytesIO(clinicianDescriptor_file), 'Sheet0', names=['concept_id', 'cpt_code', 'clinician_descriptor_id', 'clinician_descriptor'])
    df_cd.to_csv('ClinicianDescriptor.csv', sep='\t')
    push_to_s3()

def push_to_s3():
    s3 = boto3.client('s3')

    try:
        s3.upload_file('ClinicianDescriptor.csv', 'ama-hsg-datalabs-datalake-ingestion-sandbox', 'ClinicianDescriptor.csv')
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False

def main():
    descriptors_to_csv()

if __name__ == "__main__":
    main()
