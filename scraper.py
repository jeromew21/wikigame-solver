from urllib.parse import urljoin
from bs4 import BeautifulSoup, SoupStrainer
import requests
import time


BASE_URL = "https://en.wikipedia.org/"

def valid_page(href):
    """Given a HREF attribute, determine if href is a valid page, and return a cleaned version of it. Returns NONE if not valid page."""
    if any((
        href.startswith("//"),
        href.startswith("#cite"),
        href.startswith("http"),
        href.startswith("/wiki/Template:"),
        href.startswith("/wiki/Special:"),
        href.startswith("/wiki/Wikipedia:"),
        href.startswith("/wiki/Template_talk:"),
        href.startswith("/wiki/news:"),
        href.startswith("news:"),
        href.startswith("News:"),
        href.startswith("/wiki/Talk:"),
        href.startswith("/wiki/File:"),
        href.startswith("/wiki/Category:"),
        href.startswith("/wiki/Wikipedia:"),
        href.startswith("/wiki/MediaWiki:"),
        href.startswith("/wiki/Portal:"),
        href.startswith("/wiki/Help:"),
        href.startswith("/wiki/Book:"),
        href.startswith("/w/index"),
        href.startswith("irc://"),
        href.startswith("ftp://"),
        href.startswith("mms://"),
        href.startswith("git://"),
        href.startswith("Tel:"),
        href.startswith("urn:"),
        href.startswith("sip:"),
        href.startswith("svn:"),
        len(href.strip()) == 0,
    )):
        return None
    href = href.split("#")[0] #Strip off id locators
    result = urljoin(BASE_URL, href)
    if result != BASE_URL:
        return result
    return None

def scrape(url, filter_func=valid_page):
    """Take in a url and a yields a NAME and a GENERATOR that generates urls"""
    try:
        r = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        })
    except:
        print(f"HTTP request failed for {url}")
        try: #If at first you don't succeed, try again
            time.sleep(1)
            r = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
            })
        except:
            print(f"HTTP request failed twice for {url}")
            raise Exception()
    soup = BeautifulSoup(r.text, 'lxml', parse_only=SoupStrainer(["title", "div", "a"]))
    name = soup.find("title").text[0:-12]
    def gen():
        body = soup.find("div", {"id": "bodyContent"})
        if not body:
            return
            yield
        found = []
        for a in body.findAll("a"):
            if not a.has_attr("href"): continue
            href = a["href"]
            linked = valid_page(href)
            if linked is not None:
                if linked not in found:
                    found.append(linked)
                    #print(linked)
                    yield linked
    return name, gen()

def test():
    jesus = list(scrape("https://en.wikipedia.org/wiki/Jesus"))
    len(jesus)

if __name__ == "__main__":
    test()