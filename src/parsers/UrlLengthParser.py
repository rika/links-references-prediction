from .BaseParser import BaseParser


class UrlLengthParser(BaseParser):
    def parse(self, url, html):
        return len(url)
