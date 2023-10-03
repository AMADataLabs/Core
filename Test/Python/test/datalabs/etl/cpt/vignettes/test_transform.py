""" source: datalabs.etl.cpt.vignettes.transform """
import logging
import pytest

import pandas

from   datalabs.etl.cpt.vignettes.transform import VignettesTransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

# pylint: disable=redefined-outer-name, protected-access
def test_parse_data(transformer, data):
    parsed_data = transformer._parse_data(data)

    assert len(parsed_data) == 4

def test_match_datasets(transformer, data):
    vignettes, codes, hcpcs_codes, administrative_codes = transformer._parse_data(data)

    matched_data = transformer._match_datasets(vignettes, codes, hcpcs_codes, administrative_codes)

    assert isinstance(matched_data, pandas.DataFrame)
    assert 'concept_id' in matched_data.columns
    assert not matched_data['cpt_code'].isnull().any()
    assert not matched_data['concept_id'].isnull().any()
    assert len(vignettes) == len(matched_data)

    return matched_data

def test_create_vignettes_mappings(transformer, data):
    data = test_match_datasets(transformer, data)

    cleaned_data = transformer._clean_data(data)

    mappings = transformer._create_vignettes_mappings(cleaned_data)

    assert isinstance(mappings[0], dict)

@pytest.fixture
def data(vignettes_data, comprehensive_data, hcpcs_data, administrative_data):

    data = [vignettes_data,
            comprehensive_data,
            hcpcs_data,
            administrative_data
    ]

    return data

@pytest.fixture
def parameters(data):
    return dict(
        data=data,
        EXECUTION_TIME='2023-10-02T21:30:00.000000'
    )

@pytest.fixture
def vignettes_data():
    data =b"""\
Header1|
Header2|
Header3|
Header4|
Header5|
Header6|
Header7|
Header8|
Header9|
Header10|
Header11|
Header12|
Header13|
Header14|
Header15|
Header16|
Header17|
Header18|
Header19|
Header20|
Header21|
Header22|
Header23|
Header24|
Header25|
Header26|
Header27|
Header28|
Header29|
Header30|
Header31|
111|fake description|blah|blah|blah
222|fun|blast|awesome|cool|blah
777|testing|is|really|fun|Value12
888|hello|world|Value16|Value17|Value18
666|Value20|Value21|Value22|Value23|Value24
"""

    return data

@pytest.fixture
def comprehensive_data():
    data = b"""\
Concept Id\tCPT Code
1\t111
2\t222
3\t333
4\t444
5\t555
"""

    return data

@pytest.fixture
def hcpcs_data():
    data = b"""\
Concept Id\tHCPCS II Code
1\t666
2\t786
3\t6766
4\t676
5\t6854
"""

    return data
    
@pytest.fixture
def administrative_data():
    data = b"""\
Concept Id\tCode
7\t777
8\t888
9\t999
10\t1010
11\t1111
"""

    return data

@pytest.fixture
def transformer(parameters):
    return VignettesTransformerTask(parameters)
