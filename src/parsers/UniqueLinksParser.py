import re
from bs4 import BeautifulSoup as BS
from .BaseParser import BaseParser


class UniqueLinksParser(BaseParser):
    def parse(self, url, html):
        soup = BS(html, "html.parser")
        links = [e.get('href') for e in soup.find_all('a') if e]

        # ignore querystring and anchors
        links = [re.search('[^?#]*', link).group(0) for link in links if link]

        # remove invalid links
        links = [link for link in links if self.__valid_url(link)]

        # remove duplicates
        links = list(set(links))

        # handle internal links
        def map_func(link):
            return (url + link.rstrip('/')) if (link.startswith('/')) else link.rstrip('/')

        links = list(map(map_func, links))

        return links

    def __valid_url(self, url):
        return url.startswith(('http', '/'))
