import re
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup as BS

Pattern = type(re.compile('', 0))


class Scraper:
    def __init__(self, url):
        self.url = url.rstrip('/')

    def get_links(self) -> list:
        response = self.__retry_get_url(self.url)

        # consider only 200 (no redirects)
        if response.status_code == 200:
            html = str(response.text)
            return self.__parse_links(html)
        else:
            return []

    def __parse_links(self, html) -> list:
        soup = BS(html, "html.parser")
        links = [e.get('href') for e in soup.find_all('a')]

        # remove empty links
        links = [link for link in links if self.__valid_url(link)]

        # ignore querystring
        links = [re.search('[^?]*', link).group(0) for link in links]

        # remove duplicates
        links = list(set(links))

        # handle internal links
        def map_func(link):
            link = link.rstrip('/')
            return self.url + link if (link.startswith('/')) else link

        links = list(map(map_func, links))

        return links

    def __valid_url(self, url):
        return url is not None and url.startswith(('http', '/'))

    def __retry_get_url(self, url):
        retry_strategy = Retry(
            total=3,
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session.get(url)
