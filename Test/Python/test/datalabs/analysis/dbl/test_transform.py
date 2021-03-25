""" Source: Sandbox/DBL/transform.py """
import os

import pytest
#import ???


@pytest.mark.skipif(
    os.getenv('RUN_INTEGRATION_TESTS') != 'True',
    reason="Normally skip integration tests to increase testing speed."
)
def test_transformer_works_with_sandbox_data():
    files = [
        'Sandbox/DBL/testing/2021-03-23/changefileaudit.txt'
        'Sandbox/DBL/testing/2021-03-23/ReportByFieldFrom_SAS.txt'
        'Sandbox/DBL/testing/2021-03-23/countofchangesbyfieldextract.txt'
        'Sandbox/DBL/testing/2021-03-23/recordactionextract.txt'
        'Sandbox/DBL/testing/2021-03-23/changebyrecordcount.txt'
        'Sandbox/DBL/testing/2021-03-23/PE_counts.txt'
        'Sandbox/DBL/testing/2021-03-23/TOP_counts.txt'
        'Sandbox/DBL/testing/2021-03-23/topbyPEcounts.txt'
        'Sandbox/DBL/testing/2021-03-23/PrimSpecbyMPA.txt'
        'Sandbox/DBL/testing/2021-03-23/SecSpecbyMPA.txt'
    ]

    data = []
    for file in files:
        with open(file) as f:
            data.update(f.read())  # needs to be bytes, not string

    parameters = dict(data=data)

    t = DBLReportTransformer(parameters=parameters)
    output = t._transform()[0]
    print(output)
    with open("transform_test.xlsx", "wb") as f:
        f.write(output)
