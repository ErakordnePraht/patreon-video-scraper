from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from urllib.request import urlopen
import time
import json
import subprocess
import unicodedata
import re

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def process_browser_logs_for_network_events(logs):
    """
    https://gist.github.com/rengler33/f8b9d3f26a518c08a414f6f86109863c
    Return only logs which have a method that start with "Network.response", "Network.request", or "Network.webSocket"
    since we're interested in the network events specifically.
    """
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if (
                "Network.requestWillBeSent" in log["method"] and
                "request" in log["params"].keys() and
                "https://stream.mux.com/" in log["params"]["request"]["url"]
        ):
            yield log

def get_post_title_element(element) -> WebElement:
    return element.find_elements(By.TAG_NAME, "a")[1]

def get_post_text(element):
    return get_post_title_element(element).text

def get_post_link(element):
    return get_post_title_element(element).get_attribute("href")

def create_download_file_from_link():
    logs = driver.get_log("performance")
    videolink = None
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if("Network.requestWillBeSent" in log["method"] and
            "request" in log["params"].keys() and "https://stream.mux.com/" in log["params"]["request"]["url"]):
            videolink = log["params"]["request"]["url"]
    if videolink == None:
        return False
    streamsfile = urlopen(videolink).read().decode("utf-8")
    streams = streamsfile.split("\n")

    bestVideoLinkIndex = None
    currentTier = 4

    for index, link in enumerate(streams):
        if("RESOLUTION=1920x1080" in link):
            bestVideoLinkIndex = index+1
            currentTier = 1
        elif("RESOLUTION=1280x720" in link and currentTier > 2):
            bestVideoLinkIndex = index+1
            currentTier = 2
        elif("RESOLUTION=960x540" in link and currentTier > 3):
            bestVideoLinkIndex = index+1
            currentTier = 3

    videofilecontent = urlopen(streams[bestVideoLinkIndex]).read().decode("utf-8")
    videofile = open("currentvideo.txt", "w")
    videofile.write(videofilecontent)
    videofile.close()
    return True

def download_video_from_file():
    command = f"""ffmpeg -protocol_whitelist file,http,https,tcp,tls -allowed_extensions ALL -i ./currentvideo.txt -bsf:a aac_adtstoasc -c copy videos/{slugify(driver.find_element(By.CSS_SELECTOR, "span[data-tag='post-title']").text)}.mp4"""
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

taglinks = []
sessionid = input("patreon session_id (if trying to download premium content): ")
line = input("input patreon posts link (ex: https://www.patreon.com/exampleperson/posts?filters[tag]=example) or press enter to continue: ")

while line:
    taglinks.append(line)
    line = input("input patreon posts link (ex: https://www.patreon.com/exampleperson/posts?filters[tag]=example) or press enter to continue: ")

capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

driver = webdriver.Chrome(desired_capabilities=capabilities)
driver.get("https://www.patreon.com/")
driver.add_cookie({"name": "session_id", "value": sessionid})

for tag in taglinks:
    links = []
    driver.get(tag)
    time.sleep(5)

    posts = driver.find_elements(By.TAG_NAME, "ul")[3].find_elements(By.TAG_NAME, "li")

    previousFinalPost = get_post_text(posts[-1])

    while(True):
        for post in posts:
            if (get_post_link(post) not in links):
                links.append(get_post_link(post))
        try:
            loadmore = driver.find_element(By.XPATH, "//*[text()='Load more']/..")
            loadmore.click()
        except:
            break
        time.sleep(5)
        posts = driver.find_elements(By.TAG_NAME, "ul")[3].find_elements(By.TAG_NAME, "li")
        if(get_post_text(posts[-1]) == previousFinalPost):
            break
        previousFinalPost = get_post_text(posts[-1])

    print(f"posts found under {tag}: {len(links)}")

    for link in links:
        driver.get(link)
        time.sleep(3)
        success = create_download_file_from_link()
        if not success:
            print("no video found: " + link)
            continue
        download_video_from_file()
        print("video downloaded: " + link)

print("done")