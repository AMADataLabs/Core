import tempfile

import pytest


@pytest.fixture
def extractor_directory():
    with tempfile.TemporaryDirectory() as temp_directory:
        yield temp_directory


# pylint: disable=line-too-long, redefined-outer-name
@pytest.fixture
def extractor_file(extractor_directory):
    prefix = 'PhysicianProfessionalDataFile_2020120'

    with tempfile.NamedTemporaryFile(dir=extractor_directory, prefix=prefix+'1'):
        with tempfile.NamedTemporaryFile(dir=extractor_directory, prefix=prefix+'2') as file:
            file.write(
                """98765432109|A|1|2|MICHAEL A FOX MD|FOX|MICHAEL|ANDREW|||1234 SOMELANE LN|SOMETOWN|AL|35242|7463|R077||117|01|!|35242|7463|99|6|!|3|6|5|0127|03|1|B|1|13820||1|1972|SOMETOWN|AL|US1|1||||020|011|EM|FM|OFF|||Y||06302003||||||11|0440|001|02|2000|||Y|11122009||||||||||||||
98765432108|A|1|3|EDWARD J OLMOS MD|OLMOS|EDWARD|JAMES|||1234 SOMEDRIVE DR|SOMETOWN|NC|27617|7408|R077||183|37|!|27617|7408|01|7|!|3|5|6|0537|09|3|A|1|39580||1|1955|SOMETOWN|GA|US1|2||||100|110|FOP|US|NCL|||||10312006||||||48|9502|001|02|2001||||||1234 SOMEDRIVE DR|SOMETOWN|NC|27617|7408|R077|||||||
98765432107|A|1|1|J MICHAEL STRACZYNSKI MD|STRACZYNSKI|JOSEPH|MICHAEL|||1234 SOMEBOULEVARD BLVD|SOMETOWN|NC|28203|5812|C007||119|37|!|28203|5812|00|9|!|3|5|6|0035|00|1|A|1|16740||1|1973|SOMETOWN|MS|US1|1|8282544337||8282522245|020|030|PD|US|OFF|||Y||06302003||||||36|0291|001|02|2000|||||AAA PEDIATRIC ASSOC|1234 SOMEDRIVE DR|SOMETOWN|NC|28805|1262|C082|||||||""".encode('UTF-8')
            )
            file.flush()

            yield file.name


@pytest.fixture
def loader_directory():
    with tempfile.TemporaryDirectory() as temp_directory:
        yield temp_directory
