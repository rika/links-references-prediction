from .BaseParser import BaseParser


class CharactersCountParser(BaseParser):
    def parse(self, url, html):
        return len(html)
