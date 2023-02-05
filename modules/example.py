
from bs4 import BeautifulSoup
from modules.base import SislyBase

class SislyExample(SislyBase):
    def __init__(self, URL, page_limit=1000, config={}):
        super().__init__(URL, "/path/to/files",  page_limit, [{"name": "LoginToken", "value": ""}], config=config)

    imgs = []
    vids = []
    def scan_for_media(self):
        
        while self.scroll_to_bottom(2, 0.3333):
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            for parent in soup.find_all(class_="post_image"):
                a_tag = parent.find("img")
                link = a_tag.attrs['src'].replace("_300.jpg", ".jpg")
                if link not in self.imgs:
                    self.imgs.append(link)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            for parent in soup.find_all(class_="post_video"):
                a_tag = parent.find("video")
                try:
                    link = a_tag.attrs['src']
                except:
                    link = None
                if link is None or len(link) == 0:
                    try:
                        link = a_tag.attrs['source']
                    except:
                        pass
                a_tag = parent.find("source")
                try:
                    link = a_tag.attrs['src']
                except:
                    link = None
                if link is not None:
                    if link not in self.vids:
                        self.vids.append(link)
    def queue_all_media(self):
        print("["+self.SITE+"] Building final list...")
        if self.vids is None:
            self.vids = []
        if self.imgs is None:
            self.imgs = []
        self.imgs.extend(self.vids)
        #print(self.imgs)
        self.imgs.sort()
        self.DB.update_log(self.DB_ID, status="SENDING_TO_DOWNLOADER")
        print("["+self.SITE+"] Adding list to downloader...")
        print("["+self.SITE+"] Adding " + str(len(self.imgs)) + " to downloader...")
        for i in self.imgs:
            if self.DB.count_media_log(url=i) < 1:
                self.DB.insert_media_log(self.SITE, i)
                self.aria2.addUri([i], {"dir": self.DIR})
            else:
                print("["+self.SITE+"] Skipping " + str(i) + ". Already exited in database.")
        self.DB.update_log(self.DB_ID, status="SENT_TO_DOWNLOADER")

