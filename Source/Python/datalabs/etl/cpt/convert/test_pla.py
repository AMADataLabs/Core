import boto3
import os
import pandas as pd
import tempfile
import pytest


@pytest.fixture(scope='module')
def csv_file():
    s3 = boto3.client('s3')
    with tempfile.NamedTemporaryFile(mode='r+') as temp:
        s3.download_file(os.environ['processed_bucket'], 'pla.csv', temp.name)
    csv_file = temp.name
    return csv_file


def test_sample_codes(csv_file):
    sample_codes = ['0001U', '0002U', '0003U', '0005U', '0007U', '0008U', '0009U', '0010U', '0011U', '0012U']
    df = pd.read_csv(csv_file, sep='\t', nrows=10)
    tested_codes = df['pla_code'].tolist()
    print(tested_codes)
    assert tested_codes == sample_codes


def test_short_description(csv_file):
    sample_descriptions = ['RBC DNA HEA 35 AG 11 BLD GRP', 'ONC CLRCT 3 UR METAB ALG PLP',
                           'ONC OVAR 5 PRTN SER ALG SCOR', 'ONCO PRST8 3 GENE UR ALG', 'RX TEST PRSMV UR W/DEF CONF',
                           'HPYLORI DETCJ ABX RSTNC DNA', 'ONC BRST CA ERBB2 AMP/NONAMP',
                           'NFCT DS STRN TYP WHL GEN SEQ', 'RX MNTR LC-MS/MS ORAL FLUID',
                           'GERMLN DO GENE REARGMT DETCJ']
    df = pd.read_csv(csv_file, sep='\t', nrows=10)
    tested_descriptions = df['short_description'].tolist()
    print(tested_descriptions)

    assert tested_descriptions == sample_descriptions


def test_manufacturer_name(csv_file):
    sample_names = ['Immucor, Inc', 'Metabolomic Technologies Inc', 'Vermillion, Inc', 'Exosome Diagnostics, Inc',
                    'Genotox Laboratories LTD', 'American Molecular Laboratories, Inc', 'PacificDx', 'Mayo Clinic',
                    'Cordant Health Solutions', 'Mayo Clinic']
    df = pd.read_csv(csv_file, sep='\t', nrows=10)
    tested_names = df['manufacturer_name'].tolist()

    assert tested_names == sample_names
