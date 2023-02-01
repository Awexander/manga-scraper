from selenium import webdriver

from selenium.webdriver.firefox.options import Options as firefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from bs4 import BeautifulSoup
import json
import re
import string

def main():
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')

    driver = webdriver.Firefox(options=options)
    driver.get('https://www.asurascans.com/')

    html = BeautifulSoup(driver.page_source, 'lxml')
    listupd = html.find_all('div', attrs={'class':"luf"})
    if not listupd:
        return False

    luf = []
    for upd in listupd:
        #prevent from error nonetype did not have li properties for chapter list
        if not upd.a or not upd.ul.li:
            continue

        luf.append({
            'title': upd.a.get('title'),
            'name' : '',
            'url' : upd.a.get('href'),
            'chapter' : upd.ul.li.a.get_text().strip()
        })
        # Regular expression pattern to match the target string format
        title = upd.a.get('title')
        url = upd.a.get('href')

        name = url.split('/')
        if not name[-1]:
            manga_name = name[-2]
        else:
            manga_name = name[-1]

        title_split = title.strip(string.punctuation).lower().split(' ')
        pattern_title = "-".join(title_split)
        pattern = r"^(.*)" + pattern_title + r"(.*)$"

        match = re.match(pattern, manga_name)
        if match:
            title_matched = check_title_with_url(title, url)
            # Extract the target string from the match object
            extracted_string = match.group()
            if title_matched == title:
                print("The input string matches the target string: ", title)
            else:
                print("The input string does not match the target string")
        else:
            print("The input string does not match the expected format")

    driver.quit()
    if not luf:
        return False

    return True

    with open('asura.json', 'w', encoding='utf-8') as w:
        json.dump(luf, w, indent=4, separators=[',',':'])

def check_title_with_url(title: str, url: str) -> str:
    count = 0
    title_split = title.strip(string.punctuation).lower().split(" ")
    url_split = url.strip(string.punctuation).lower().split("-")
    for a in title_split:
        for b in url_split:
            if a == b:
                count += 1
                break
            
    if count >= len(title_split) - 1:
        return "-".join(title_split)
    
    return ""
from datetime import datetime
prevTime = datetime.now().timestamp() 

main()
'''
while True:
    if datetime.now().timestamp() - prevTime > 20:
        if not main():
            print("not ok")

        prevTime = datetime.now().timestamp()
'''