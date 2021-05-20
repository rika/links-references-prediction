import os
import pytest
import requests
from scraper import Scraper

DIR_PATH = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture()
def scraper_google(requests_mock) -> Scraper:
    url = 'https://www.google.com.br'
    with open(f'{DIR_PATH}/mocks/www.google.com.br.html', 'r') as file:
        mock = file.read()

    requests_mock.get(url, text=mock)
    return Scraper(url)


@pytest.fixture()
def scraper_404(requests_mock) -> Scraper:
    url = 'https://mock404'
    requests_mock.get(url, status_code=404)
    return Scraper(url)


@pytest.fixture()
def scraper_301(requests_mock) -> Scraper:
    url = 'https://mock301'
    requests_mock.get(url, status_code=301)
    return Scraper(url)


def test_scraper_get_links_invalid_url() -> None:
    with pytest.raises(requests.exceptions.MissingSchema):
        scraper = Scraper('invalid_url')
        scraper.get_links()


def test_scraper_google_get_links_list(scraper_google) -> None:
    links = scraper_google.get_links()
    assert isinstance(links, list)


def test_scraper_google_get_links_result(scraper_google) -> None:
    links = scraper_google.get_links()
    expected_links = [
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

    assert len(links) == len(expected_links)
    assert all([a == b for a, b in zip(sorted(links), sorted(expected_links))])


def test_scraper_404(scraper_404) -> None:
    links = scraper_404.get_links()
    assert (len(links) == 0)


def test_scraper_301(scraper_301) -> None:
    links = scraper_301.get_links()
    assert (len(links) == 0)
