import os
import pytest
import requests
from scraper import Scraper, NoStatusCode200

DIR_PATH = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture()
def scraper_google(requests_mock):
    url = 'https://www.google.com.br'
    with open(f'{DIR_PATH}/mocks/www.google.com.br.html', 'r') as file:
        mock = file.read()

    requests_mock.get(url, text=mock)
    scraper = Scraper()
    scraper.__test_url = url
    return scraper


@pytest.fixture()
def scraper_404(requests_mock):
    url = 'https://mock404'
    requests_mock.get(url, status_code=404)
    scraper = Scraper()
    scraper.__test_url = url
    return scraper


@pytest.fixture()
def scraper_301(requests_mock):
    url = 'https://mock301'
    requests_mock.get(url, status_code=301)
    scraper = Scraper()
    scraper.__test_url = url
    return scraper


def test_scraper_get_links_invalid_url():
    with pytest.raises(requests.exceptions.MissingSchema):
        scraper = Scraper()
        scraper.execute('invalid_url')


def test_scraper_google_get_links_list(scraper_google):
    html = scraper_google.execute(scraper_google.__test_url)
    with open(f'{DIR_PATH}/mocks/www.google.com.br.html', 'r') as file:
        mock = file.read()
        assert html == mock


def test_scraper_404(scraper_404):
    with pytest.raises(NoStatusCode200):
        scraper_404.execute(scraper_404.__test_url)


def test_scraper_301(scraper_301):
    with pytest.raises(NoStatusCode200):
        scraper_301.execute(scraper_301.__test_url)
