
from pyaria2 import Aria2RPC
from selenium import webdriver
from modules.db import SislyDB
from urllib.parse import urlparse
from dotenv import load_dotenv

import time
import os
class SislyBase(object):
    URL = None
    DIR = None
    ARIA2_PROTOCOL = ""
    ARIA2_HOST = ""
    ARIA2_PORT = 0
    WEBDRIVER_PROTOCOL = ""
    WEBDRIVER_HOST = ""
    WEBDRIVER_PORT = 0
    PROCESS_INTERVAL = 15
    PAGE_LIMIT = 1000
    DB_ID = None
    SITE = None
    def __init__(self,URL, DIR, page_limit=1000, COOKIES=[], process_interval=15, config={}):

        load_dotenv()  
        self.DB = SislyDB()
        self.DB.connect()

        self.URL = URL

        self.SITE = urlparse(self.URL).netloc        

        print("["+self.SITE+"] Starting download of " + URL)

        print("["+self.SITE+"] Loading Config...")
        print("["+self.SITE+"] Using Config: " + str(config))
        self.load_config(config)
        print("["+self.SITE+"] If a config was not set, the default was used.")

        # initialization, these are the default values
        print("["+self.SITE+"] Initializing Aria2...")
        url = self.ARIA2_PROTOCOL+"://"+self.ARIA2_HOST+":"+str(self.ARIA2_PORT)
        self.aria2 = Aria2RPC(url=url+"/rpc", token=os.environ.get("ARIA2_TOKEN"))
        self.PROCESS_INTERVAL = process_interval
        self.PAGE_LIMIT = page_limit
        #aria2.addUri(["https://www.google.com/images/logo.png"], {"dir": "/data/Downloads/Nt/"})

        self.init_driver(URL, COOKIES)

        print("["+self.SITE+"] Reload...")
        self.driver.get(URL)
        self.DB_ID = self.DB.insert_log(URL, "SCROLLING_PAGES")
    def load_config(self, config):
        self.ARIA2_PROTOCOL = config["aria2"]["protocol"] or "http"
        self.ARIA2_HOST = config["aria2"]["host"] or "127.0.0.1"
        self.ARIA2_PORT = config["aria2"]["port"] or 6800
        self.WEBDRIVER_PROTOCOL = config["webdriver"]["protocol"] or "http"
        self.WEBDRIVER_HOST = config["webdriver"]["host"] or "127.0.0.1"
        self.WEBDRIVER_PORT = config["webdriver"]["port"] or 4444
    def init_driver(self, URL="https://www.google.com/", COOKIES=[]):
        capabilities = {
            "browserName": "chrome",
            "browserVersion": "latest",
            "selenoid:options": {
                "enableVNC": True,
                "enableVideo": False
            }
        }
        options = webdriver.ChromeOptions()
        options.add_argument("--start-fullscreen")
        options.add_argument("--blink-settings=imagesEnabled=false")

        print("["+self.SITE+"] Initializing WebDriver")
        self.driver = webdriver.Remote(
            command_executor=self.WEBDRIVER_PROTOCOL+"://"+self.WEBDRIVER_HOST+":"+str(self.WEBDRIVER_PORT)+"/wd/hub",
            desired_capabilities=capabilities, options=options)

        print("["+self.SITE+"] Setting fullscreen")
        self.driver.fullscreen_window()

        print("["+self.SITE+"] First load...")
        self.driver.get(URL)

        print("["+self.SITE+"] Inject cookies...")
        for cookie in COOKIES:
            self.driver.add_cookie(cookie)
    i = 1
    time_ellapsed = 0
    end_of_screen = False
    def scroll_to_bottom(self, delay=5, ri_rate=0.2):
        #time.sleep(delay + 2)  # Allow 2 seconds for the web page to open
        scroll_pause_time = delay # You can set your own pause time. My laptop is a bit slow so I use 1 sec
        screen_height = self.driver.execute_script("return window.screen.height;")   # get the screen height of the web
        start = time.time()
        if int(self.PAGE_LIMIT) < int(self.i):
            print("["+self.SITE+"] Page limit reached")
            return False
        print("["+self.SITE+"] Loading page " + str(self.i))
        self.DB.update_log(self.DB_ID, current_page=self.i)
        # scroll one screen height each time
        offset = 0.4 * 1080
        ri = 1
        while True:
            self.driver.execute_script("window.scrollTo(0, {screen_height}*{i} - {offset} * {ri});".format(screen_height=screen_height, i=self.i, offset=offset, ri=ri))  
            time.sleep(int((ri * 6) / 2))
            ri = ri - ri_rate
            if ri <= 0:
                break
        self.i += 1
        time.sleep(scroll_pause_time)
        # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
        scroll_height = self.driver.execute_script("return document.body.scrollHeight;")  
        # Break the loop when the height we need to scroll to is larger than the total scroll height
        self.time_ellapsed = time.time() - start
        if (screen_height) * self.i > scroll_height:
            if not self.end_of_screen:
                start = time.time() 
            self.end_of_screen = True

            if self.time_ellapsed > 20:
                print("["+self.SITE+"] End Of Page - Break!")
                return False
        return True

    def scan_for_media(self):
        pass

    def queue_all_media(self):
        pass

    def get_download_folder(self):
        return self.DIR

    def cleanup(self, _url):
        return self.DB.queue_delete(_url)

    def run(self):
        try:
            self.scan_for_media()
        except:
            pass
        self.queue_all_media()
