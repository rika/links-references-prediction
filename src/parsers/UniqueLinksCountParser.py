from .UniqueLinksParser import UniqueLinksParser


class UniqueLinksCountParser(UniqueLinksParser):
    def parse(self, url, html) -> int:
        links = super().parse(url, html)
        return len(links)
