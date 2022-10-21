""" source: datalabs.etl.http.extract """
import pytest

from   datalabs.etl.http.extract import HTTPFileExtractorTask, HTTPFileListExtractorTask


# pylint: disable=redefined-outer-name, protected-access
def test_urls_parameter_is_parsed_correctly(parameters, expected_urls):
    extractor = HTTPFileExtractorTask(parameters)
    urls = extractor._get_files()

    assert len(urls) == 3

    for url, expected_url in zip(urls, expected_urls):
        assert url == expected_url


# pylint: disable=redefined-outer-name, protected-access
def test_url_list_data_is_parsed_correctly(parameters, data, expected_urls):
    parameters.pop('URLS')

    extractor = HTTPFileListExtractorTask(parameters, data)
    urls = extractor._get_files()

    assert len(urls) == 3

    for url, expected_url in zip(urls, expected_urls):
        assert url == expected_url


@pytest.fixture
def expected_urls():
    return [
        'https://my.bogus.domain.test/hardee',
        'https://your.bogus.domain.test/harhar',
        'https://mystical.ginger.prince.com/faces/everywhere'
    ]


@pytest.fixture
def parameters():
    # pylint: disable=line-too-long
    return dict(
        URLS='https://my.bogus.domain.test/hardee,https://your.bogus.domain.test/harhar,https://mystical.ginger.prince.com/faces/everywhere',
        EXECUTION_TIME='1997-08-29T07:14:00'
    )


@pytest.fixture
def data():
    return [
        '''https://my.bogus.domain.test/hardee
        https://your.bogus.domain.test/harhar'''.encode(),
        'https://mystical.ginger.prince.com/faces/everywhere'.encode(),
    ]
