import os
import pytest
from parsers import \
    CharactersCountParser, \
    ImagesCountParser, \
    UniqueLinksCountParser, \
    UniqueLinksParser, \
    UrlLengthParser, \
    WordsCountParser


DIR_PATH = os.path.dirname(os.path.realpath(__file__))
GOOGLE_LINKS = [
    'http://www.google.com.br/history/optout',
    'https://accounts.google.com/ServiceLogin',
    'https://drive.google.com',
    'https://mail.google.com/mail',
    'https://maps.google.com.br/maps',
    'https://news.google.com',
    'https://play.google.com',
    'https://www.google.com.br/advanced_search',
    'https://www.google.com.br/imghp',
    'https://www.google.com.br/intl/pt-BR/about.html',
    'https://www.google.com.br/intl/pt-BR/about/products',
    'https://www.google.com.br/intl/pt-BR/ads',
    'https://www.google.com.br/intl/pt-BR/policies/privacy',
    'https://www.google.com.br/intl/pt-BR/policies/terms',
    'https://www.google.com.br/preferences',
    'https://www.google.com.br/services',
    'https://www.google.com.br/setprefdomain',
    'https://www.youtube.com'
]


@pytest.fixture()
def mock_google_html():
    mock_url = 'https://www.google.com.br'
    with open(f'{DIR_PATH}/mocks/www.google.com.br.html', 'r') as file:
        mock_html = file.read()

    return (mock_url, mock_html)


def test_parse_unique_links(mock_google_html):
    mock_url, mock_html = mock_google_html
    parser = UniqueLinksParser()
    links = parser.parse(mock_url, mock_html)
    expected_links = GOOGLE_LINKS

    assert len(links) == len(expected_links)
    assert all([a == b for a, b in zip(sorted(links), sorted(expected_links))])


def test_parse_character_count(mock_google_html):
    mock_url, mock_html = mock_google_html
    parser = CharactersCountParser()
    count = parser.parse(mock_url, mock_html)
    assert count == len(mock_html)


def test_parse_image_count(mock_google_html):
    mock_url, mock_html = mock_google_html
    parser = ImagesCountParser()
    count = parser.parse(mock_url, mock_html)
    assert count == 2


def test_parse_unique_links_count(mock_google_html):
    mock_url, mock_html = mock_google_html
    parser = UniqueLinksCountParser()
    count = parser.parse(mock_url, mock_html)
    assert count == len(GOOGLE_LINKS)


def test_parse_url_length(mock_google_html):
    mock_url, mock_html = mock_google_html
    parser = UrlLengthParser()
    count = parser.parse(mock_url, mock_html)
    assert count == len(mock_url)


def test_parse_words_count(mock_google_html):
    mock_url, mock_html = mock_google_html
    parser = WordsCountParser()
    count = parser.parse(mock_url, mock_html)
    assert count == len(mock_html.split(' '))
