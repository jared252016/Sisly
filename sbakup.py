#!/usr/bin/python3
from pyaria2 import Aria2RPC
from selenium import webdriver
import sys
import time
from bs4 import BeautifulSoup

# initialization, these are the default values
print("Initializing Aria2...")
aria2 = Aria2RPC(url="http://192.168.50.7:6800/rpc", token='P3TERX')

#aria2.addUri(["https://www.google.com/images/logo.png"], {"dir": "/data/Downloads/NewTumbl/"})
 
capabilities = {
    "browserName": "chrome",
    "browserVersion": "90.0",
    "selenoid:options": {
        "enableVNC": True,
        "enableVideo": False
    }
}
options = webdriver.ChromeOptions()
options.add_argument("--start-fullscreen")
options.add_argument("--blink-settings=imagesEnabled=false")

print("Initializing WebDriver")
driver = webdriver.Remote(
    command_executor="http://192.168.50.7:4444/wd/hub",
    desired_capabilities=capabilities, options=options)

driver.fullscreen_window()
driver.get("https://" + sys.argv[1].replace("https://", "").replace("http://", ""))

driver.add_cookie({"name": "LoginToken", "value": "FzCWMJL_AG_Eg11zFAo6dXgZWWQXOOpJxo1MLgoxVFCm6Mhj"})

driver.get("https://" + sys.argv[1].replace("https://", "").replace("http://", ""))

time.sleep(5)  # Allow 2 seconds for the web page to open
scroll_pause_time = 3 # You can set your own pause time. My laptop is a bit slow so I use 1 sec
screen_height = driver.execute_script("return window.screen.height;")   # get the screen height of the web
i = 1

while True:
    # scroll one screen height each time
    driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
    i += 1
    time.sleep(scroll_pause_time)
    # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
    scroll_height = driver.execute_script("return document.body.scrollHeight;")  
    # Break the loop when the height we need to scroll to is larger than the total scroll height
    if (screen_height) * i > scroll_height:
        print("End Of Page - Break!")
        break 


##### Extract Reddit URLs #####
imgs = []
soup = BeautifulSoup(driver.page_source, "html.parser")
for parent in soup.find_all(class_="post_image"):
    a_tag = parent.find("img")
    link = a_tag.attrs['src'].replace("_300.jpg", ".jpg")
    imgs.append(link)
#aria2.add(imgs)
#print(imgs)


##### Extract Reddit URLs #####
vids = []
soup = BeautifulSoup(driver.page_source, "html.parser")
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
        vids.append(link)
#aria2.addUri(vids, {"dir":"/data/Downloads/NewTumbl/"})
#print(vids)

print("Building final list...")
if vids is None:
    vids = []
if imgs is None:
    imgs = []
imgs.extend(vids)
print(imgs)
imgs.sort()
print("Adding list to downloader...")
print("Adding " + str(len(imgs)) + " to downloader...")
for i in imgs:
    aria2.addUri([i], {"dir": "/data/Downloads/NewTumbl/"})
