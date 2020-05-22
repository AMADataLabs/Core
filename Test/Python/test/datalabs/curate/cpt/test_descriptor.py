import logging
import pytest

from   datalabs.curate.cpt.descriptor import ConsumerDescriptorParser, ClinicianDescriptorParser

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_consumer_descriptor_parser(consumer_descriptor_text):
    parser = ConsumerDescriptorParser()

    data = parser.parse(consumer_descriptor_text)

    LOGGER.debug('Consumer Descriptor Data: \n%s', data)
    assert len(data) == 2

    assert data['concept_id'][0] == '1002798'
    assert data['concept_id'][1] == '1002799'

    assert data['cpt_code'][0] == '00100'
    assert data['cpt_code'][1] == '00102'

    for descriptor in data['consumer_descriptor']:
        assert descriptor.startswith('Anesthesia for procedure')

def test_clinician_descriptor_parser(clinician_descriptor_text):
    parser = ClinicianDescriptorParser()

    data = parser.parse(clinician_descriptor_text)

    LOGGER.debug('Clinician Descriptor Data: \n%s', data)

    assert data['concept_id'][0] == '1002798'
    assert data['concept_id'][1] == '1002798'

    assert data['cpt_code'][0] == '00100'
    assert data['cpt_code'][1] == '00100'

    assert data['clinician_descriptor_id'][0] == '10000002'
    assert data['clinician_descriptor_id'][1] == '10031990'

    for descriptor in data['clinician_descriptor']:
        assert descriptor.startswith('Anesthesia for procedure')


@pytest.fixture
def consumer_descriptor_text():
    return """Concept Id\tCPT Code\tConsumer Friendly Descriptor
1002798\t00100\tAnesthesia for procedure on salivary gland with biopsy
1002799\t00102\tAnesthesia for procedure to repair lip defect present at birth
"""


@pytest.fixture
def clinician_descriptor_text():
    return """Concept Id\tCPT Code\tClinician Descriptor Id\tClinician Descriptor
1002798\t00100\t10000002\tAnesthesia for procedure on salivary gland with biopsy
1002798\t00100\t10031990\tAnesthesia for procedure on salivary gland
"""
