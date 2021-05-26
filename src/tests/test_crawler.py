import os
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, asc
from pyspark.sql.types import StringType
from crawler import Crawler

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

URL_A = 'https://a.mock'  # [B, C]
URL_B = 'https://b.mock'  # [B, C]
URL_C = 'https://c.mock'  # [B, A]


def __link(url):
    return f'<a href="{url}"></a>'


def __mock_html(urls):
    links = ''.join(map(__link, urls))
    return f'<html>{links}</html>'


HTML_A = __mock_html([URL_B, URL_C])
HTML_B = __mock_html([URL_B, URL_C])
HTML_C = __mock_html([URL_B, URL_A])


@pytest.fixture(scope='session')
def spark():
    return SparkSession.builder \
        .master("local[*]") \
        .appName("test") \
        .getOrCreate()


@udf(returnType=StringType())
def mock_udf_scrap(url):
    if url == URL_A:
        return HTML_A
    elif url == URL_B:
        return HTML_B

    elif url == URL_C:
        return HTML_C
    else:
        return None


@pytest.fixture()
def crawler(spark, mocker):
    # requests_mock does not work for udfs, so we need to patch
    mocker.patch('crawler.Crawler._Crawler__udf_scrap', side_effect=mock_udf_scrap)
    return Crawler(
        spark=spark
    )


@pytest.fixture()
def mock_crawler(spark, requests_mock):
    requests_mock.get(URL_A, text=HTML_A)
    return Crawler(
        spark=spark
    )


def test_crawler_execute(spark, crawler):
    df_appearances, df_features = crawler.execute(
        urls=[URL_A],
        depth=2
    )

    expected_data_appearances = [
        (URL_A, 1),
        (URL_B, 3),
        (URL_C, 2),
    ]

    appearances = df_appearances.orderBy(asc('url')).collect()
    assert df_appearances.schema == Crawler.appearances_schema
    for a, b in zip(appearances, expected_data_appearances):
        for i in range(0, len(a)):
            assert a[i] == b[i]

    expected_data_features = [
        (URL_A, HTML_A, [URL_B, URL_C], len(HTML_A), 0, 2, len(URL_A), len(HTML_A.split(' '))),
        (URL_B, HTML_B, [URL_B, URL_C], len(HTML_B), 0, 2, len(URL_B), len(HTML_B.split(' '))),
        (URL_C, HTML_C, [URL_A, URL_B], len(HTML_C), 0, 2, len(URL_C), len(HTML_C.split(' '))),
    ]

    features = df_features.orderBy(asc('url')).collect()
    assert df_features.schema == Crawler.features_schema
    for a, b in zip(features, expected_data_features):
        for i in range(0, len(a)):
            if type(a[i]) is list:
                assert sorted(a[i]) == sorted(b[i])
            else:
                assert a[i] == b[i]


def test_crawler_get_features(spark, mock_crawler):
    df_features = mock_crawler.get_features(
        url=URL_A
    )
    features = df_features.orderBy(asc('url')).collect()[0]
    expected_data = (URL_A, HTML_A, [URL_B, URL_C], len(HTML_A), 0, 2, len(URL_A), len(HTML_A.split(' ')))

    assert df_features.schema == Crawler.features_schema
    for a, b in zip(features, expected_data):
        if type(a) is list:
            assert sorted(a) == sorted(b)
        else:
            assert a == b
