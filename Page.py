from scraper import *

class Page:
    def __init__(self, url, name=None):
        self.url = url
        self.name = name
        self._children = None

    def find_child_urls(self):
        if self._children is None:
            self.name, gen = scrape(self.url)
            #print(f"Scraped children for: '{self.name}' {self.url}")
            self._children = list(gen)
        return self._children
    

if __name__ == "__main__":
    jesus = Page("https://en.wikipedia.org/wiki/Jesus")
