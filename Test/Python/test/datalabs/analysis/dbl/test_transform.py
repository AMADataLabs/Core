""" Source: datalabs.analysis.dbl.transform """
import os

import pytest
from datalabs.analysis.dbl.transform import DBLReportTransformer


@pytest.mark.skipif(
    os.getenv('RUN_INTEGRATION_TESTS') != 'True',
    reason="Normally skip integration tests to increase testing speed."
)
# pylint: disable=protected-access, redefined-outer-name
def test_transformer_works_with_sandbox_data(input_data):
    # pylint: disable=undefined-variable
    transformer = DBLReportTransformer({}, input_data)
    output_data = transformer.run()

    assert len(output_data) == 1
    assert 70000 >= len(output_data[0]) >= 50000

    with open("transform_test.xlsx", "wb") as file:
        file.write(output_data[0])


@pytest.fixture
def input_data():
    filenames = [
        '../../../../../../Sandbox/DBL/testing/2021-03-23/changefileaudit.txt',
        '../../../../../../Sandbox/DBL/testing/2021-03-23/ReportByFieldFrom_SAS.txt',
        '../../../../../../Sandbox/DBL/testing/2021-03-23/countofchangesbyfieldextract.txt',
        '../../../../../../Sandbox/DBL/testing/2021-03-23/recordactionextract.txt',
        '../../../../../../Sandbox/DBL/testing/2021-03-23/changebyrecordcount.txt',
        '../../../../../../Sandbox/DBL/testing/2021-03-23/PE_counts.txt',
        '../../../../../../Sandbox/DBL/testing/2021-03-23/TOP_counts.txt',
        '../../../../../../Sandbox/DBL/testing/2021-03-23/topbyPEcounts.txt',
        '../../../../../../Sandbox/DBL/testing/2021-03-23/PrimSpecbyMPA.txt',
        '../../../../../../Sandbox/DBL/testing/2021-03-23/SecSpecbyMPA.txt'
    ]

    data = []
    for filename in filenames:
        with open(filename, 'rb') as file:
            data.append(file.read())  # needs to be bytes, not string

    return data
