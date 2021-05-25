from bs4 import BeautifulSoup as BS
from .BaseParser import BaseParser


class ImagesCountParser(BaseParser):
    def parse(self, url, html):
        soup = BS(html, "html.parser")
        imgs = soup.find_all('img')
        return len(imgs)
