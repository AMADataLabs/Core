import logging
import os
import tempfile

import pandas
import pytest

from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_data_setup_correctly(extractor_file):
    with open(extractor_file) as file:
        data = file.read()

    LOGGER.debug('Input Data: %s', data)
    assert len(data) > 0


def test_extractor_data_is_reasonable(etl):
    etl.run()

    extractor = etl._task._extractor

    LOGGER.debug('Extracted Data: %s', extractor.data)
    assert len(extractor.data) == 1

    data = extractor.data[0]
    assert len(data) == 2
    assert len(data[1].split('\n')) == 3


@pytest.fixture
def extractor_directory():
    with tempfile.TemporaryDirectory() as temp_directory:
        yield temp_directory


@pytest.fixture
def extractor_file(extractor_directory):
    with tempfile.NamedTemporaryFile(dir=extractor_directory, prefix='PhysicianProfessionalDataFile_20200101'):
        with tempfile.NamedTemporaryFile(dir=extractor_directory, prefix='PhysicianProfessionalDataFile_20201201') as file:
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


@pytest.fixture
def environment(extractor_file, loader_directory):
    current_environment = os.environ.copy()

    os.environ['TASK_WRAPPER_CLASS'] = 'datalabs.etl.task.ETLTaskWrapper'
    os.environ['TASK_CLASS'] = 'datalabs.etl.task.ETLTask'

    os.environ['EXTRACTOR_CLASS'] = 'datalabs.etl.ppd.expanded.extract.LocalPPDExtractorTask'
    os.environ['EXTRACTOR_BASEPATH'] = os.path.dirname(extractor_file)
    os.environ['EXTRACTOR_FILES'] = 'PhysicianProfessionalDataFile_*'

    os.environ['TRANSFORMER_CLASS'] = 'datalabs.etl.transform.PassThroughTransformerTask'

    os.environ['LOADER_CLASS'] = 'datalabs.etl.load.ConsoleLoaderTask'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_environment)


@pytest.fixture
def etl(environment):
    task_class = import_plugin(os.getenv('TASK_CLASS'))
    task_wrapper_class = import_plugin(os.getenv('TASK_WRAPPER_CLASS'))
    task_wrapper = task_wrapper_class(task_class, parameters={})

    return task_wrapper
