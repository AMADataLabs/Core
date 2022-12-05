""" source: datalabs.etl.sql.extract """
from   datalabs.etl.sql.jdbc.extract import SQLExtractorTask


# pylint: disable=redefined-outer-name, protected-access
def test_time_format_codes_in_queries_are_resolved():
    parameters = dict(
        SQL="SELECT * FROM foo WHERE created_at BETWEEN '%Y-%m-%d %H:%M:%S' AND '%Y-%m-%d %H:%M:%S' - interval '1 day'",
        EXECUTION_TIME="1200-12-12 12:12:12"
    )
    expected_query = "SELECT * FROM foo WHERE created_at BETWEEN '1200-12-12 12:12:12' AND '1200-12-12 12:12:12' - interval '1 day'"  # pylint: disable=line-too-long

    task = MockSQLExtractorTask(parameters)

    queries = task._split_queries(task._parameters.sql)
    resolved_queries = task._resolve_time_format_codes(queries)

    assert expected_query == resolved_queries[0]


class MockSQLExtractorTask(SQLExtractorTask):
    def _get_database(self):
        return None
