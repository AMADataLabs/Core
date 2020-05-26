import boto3
import logging
import json
import pandas as pd
import tempfile
import xml.etree.ElementTree as et

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def main():
    file = get_s3_file()
    code, long, medium, short, status, date, lab, manufacturer, published, test = extract_fields(file)
    dataframe = create_dataframe(code, long, medium, short, status, date, lab, manufacturer, published, test)
    csv_file = dataframe_to_csv(dataframe)
    push_csv(csv_file)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "done",
        }),
    }


def get_s3_file():
    s3 = boto3.client('s3')
    with tempfile.NamedTemporaryFile(mode='r+') as temp:
        s3.download_file('ama-hsg-datalabs-datalake-ingestion-sandbox',
                         'AMA/CPT/20200131/standard/Proprietary Laboratory Analyses (PLA) Codes/CPTPLA', temp.name)

    LOGGER.info('Download Successful')

    return temp.name


def extract_fields(file):
    pla_code = []
    long_description = []
    medium_description = []
    short_description = []
    code_status = []
    effective_date = []
    lab_name = []
    manufacturer_name = []
    published_date = []
    test_name = []

    tree = et.parse(file)
    root = tree.getroot()

    for c in tree.findall('plaCode'):
        pla_code.append(c.attrib.get('cdCode'))
        long_description.append(c.find('cdDesc').text)
        medium_description.append(c.find('cdMDesc').text)
        short_description.append(c.find('cdSDesc').text)
        code_status.append(c.find('cdStatus').text)
        # clinical_description = c.find('clinicalDesc').text
        # consumer_description = c.find('consumerDesc ').text
        effective_date.append(c.find('effectiveDate').text)
        lab_name.append(c.find('labName').text)
        manufacturer_name.append(c.find('manufacturerName').text)
        published_date.append(c.find('publishDate').text)
        test_name.append(c.find('testName').text)

    return pla_code, long_description, medium_description, short_description, code_status, effective_date, lab_name, manufacturer_name, published_date, test_name


def create_dataframe(code, long, medium, short, status, date, lab, manufacturer, published, test):
    df = pd.DataFrame(list(zip(code, long, medium, short, status, date, lab, manufacturer, published, test)),
                      columns=['pla_code', 'long_description', 'medium_description', 'short_description', 'code_status',
                               'effective_date', 'lab_name', 'manufacturer_name', 'published_date', 'test_name'])

    LOGGER.info('Dataframe created')

    return df


def dataframe_to_csv(df):
    with tempfile.NamedTemporaryFile() as temp:
        df.to_csv(temp.name + '.csv', sep='\t')

    LOGGER.info('CSV Created')

    return temp.name


def push_csv(file):
    s3 = boto3.client('s3')
    s3.upload_file(file+'.csv', 'ama-hsg-datalabs-datalake-processed-sandbox', 'pla.csv')

    LOGGER.info('Upload Successful')


main()
