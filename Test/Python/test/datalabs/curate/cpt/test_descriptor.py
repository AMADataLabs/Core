import logging
import pytest

import datalabs.curate.cpt.descriptor as desc

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=protected-access
def test_long_descriptor_header_removal(long_descriptor_text):
    parser = desc.LongDescriptorParser()

    headerless_text = parser._remove_header(long_descriptor_text)

    lines = headerless_text.splitlines()

    assert len(lines) == 2

    for line in lines:
        assert line.startswith('0010')


def test_long_descriptor_parser(long_descriptor_text):
    parser = desc.LongDescriptorParser()

    data = parser.parse(long_descriptor_text)

    assert len(data) == 2

    assert data['cpt_code'][0] == '00100'
    assert data['cpt_code'][1] == '00102'


def test_consumer_descriptor_parser(consumer_descriptor_text):
    parser = desc.ConsumerDescriptorParser()

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
    parser = desc.ClinicianDescriptorParser()

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
def long_descriptor_text():
    return """To purchase additional CPT products, contact the American Medical
Association customer service at 800-621-8335.

To request a license for distribution of products with CPT content, please
see our Web site at www.ama-assn.org/go/cpt or contact the American
Medical Association Intellectual Property Services, 330 N. Wabash Ave., Suite 39300, 
Chicago, IL 60611-5885, 312 464-5022.

00100\tAnesthesia for procedures on salivary glands, including biopsy
00102\tAnesthesia for procedures involving plastic repair of cleft lip
"""


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
