#!/bin/python3
import sys
import os
from urllib.parse import urlparse
from modules.base import SislyBase
from modules.example import SislyExample
from dotenv import load_dotenv


class Sisly:
    OG_URL = None
    URI = None
    URL = None
    config = None
    instance = None
    def __init__(self, _url) -> None:
        self.OG_URL = _url
        self.URI = urlparse(_url)
        self.URL = '{uri.scheme}://{uri.netloc}'.format(uri=self.URI)
        load_dotenv()
        self.config = {
            'aria2': {
                'protocol': os.getenv("ARIA2_PROTOCOL"),
                'host': os.getenv("ARIA2_HOST"),
                'port': int(os.getenv("ARIA2_PORT"))
            },
            "webdriver": {
                'protocol': os.getenv("WEBDRIVER_PROTOCOL"),
                'host': os.getenv("WEBDRIVER_HOST"),
                'port': int(os.getenv("WEBDRIVER_PORT"))
            }
        }
        if "example.com" in self.URI.netloc:
            self.instance = SislyExample(self.URL, config=self.config)

    def run(self):
        self.instance.run()
        if self.instance.cleanup(self.OG_URL):
            print("Removed " + self.OG_URL + " from queue.")
        else:
            print("Nothing to clean up for url: " + self.OG_URL)

if __name__ == "__main__":
    print("Sisly v0.8.0")
    print("")

    if len(sys.argv) == 1:
        print("Usage: sisly[.py] [blog]")
        exit()
    s = Sisly(sys.argv[1])
    s.run()