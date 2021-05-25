import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class NoStatusCode200(Exception):
    pass


class Scraper:
    def execute(self, url, parser=None, default=None) -> list:
        response = self.__retry_get_url(url)

        # consider only 200 (no redirects)
        if response.status_code == 200:
            html = str(response.text)
            return html
        else:
            raise NoStatusCode200()

    def __retry_get_url(self, url):
        retry_strategy = Retry(
            total=3,
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session.get(url, allow_redirects=False)
