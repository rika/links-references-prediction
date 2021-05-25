from .BaseParser import BaseParser


class WordsCountParser(BaseParser):
    def parse(self, url, html):
        return len(html.split(' '))
