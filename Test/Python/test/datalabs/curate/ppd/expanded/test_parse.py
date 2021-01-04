""" source: datalabs.curate.ppd.expanded.parse """
import logging
import pytest

import datalabs.curate.ppd.expanded.parse as parse

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name
def test_physician_data_is_parsed(physician_data):
    parser = parse.ExpandedPPDParser()
    data = parser.parse(physician_data)

    LOGGER.debug('Parsed Data: \n%s', data)
    assert len(data) == 3


# pylint: disable=line-too-long
@pytest.fixture
def physician_data():
    return \
        """98765432109|A|1|2|MICHAEL A FOX MD|FOX|MICHAEL|ANDREW|||1234 SOMELANE LN|SOMETOWN|AL|35242|7463|R077||117|01|!|35242|7463|99|6|!|3|6|5|0127|03|1|B|1|13820||1|1972|SOMETOWN|AL|US1|1||||020|011|EM|FM|OFF|||Y||06302003||||||11|0440|001|02|2000|||Y|11122009||||||||||||||
98765432108|A|1|3|EDWARD J OLMOS MD|OLMOS|EDWARD|JAMES|||1234 SOMEDRIVE DR|SOMETOWN|NC|27617|7408|R077||183|37|!|27617|7408|01|7|!|3|5|6|0537|09|3|A|1|39580||1|1955|SOMETOWN|GA|US1|2||||100|110|FOP|US|NCL|||||10312006||||||48|9502|001|02|2001||||||1234 SOMEDRIVE DR|SOMETOWN|NC|27617|7408|R077|||||||
98765432107|A|1|1|J MICHAEL STRACZYNSKI MD|STRACZYNSKI|JOSEPH|MICHAEL|||1234 SOMEBOULEVARD BLVD|SOMETOWN|NC|28203|5812|C007||119|37|!|28203|5812|00|9|!|3|5|6|0035|00|1|A|1|16740||1|1973|SOMETOWN|MS|US1|1|8282544337||8282522245|020|030|PD|US|OFF|||Y||06302003||||||36|0291|001|02|2000|||||AAA PEDIATRIC ASSOC|1234 SOMEDRIVE DR|SOMETOWN|NC|28805|1262|C082|||||||
"""
