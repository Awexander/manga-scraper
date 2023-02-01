
from bs4 import BeautifulSoup
from selenium import webdriver

file = '/home/awexander/Documents/code/manga/asura.gg.html'
'''
options = webdriver.FirefoxOptions()
options.add_argument('--headless')
options.add_argument('--profile-root /home/awexander/Documents/code/manga/webdriver/profile')
driver = webdriver.Firefox(options=options)
'''

options = webdriver.FirefoxOptions()
options.add_argument('--headless')
options.add_argument('--connect-existing')
# Instantiate a remote WebDriver
driver = webdriver.Remote(
   command_executor='http://0.0.0.0:4444',
   options=options
)

''' 
with open(file, 'r') as r:
    if not html:
        print('invalid html')
'''
file = driver.get('https://asura.gg')
html = BeautifulSoup(driver.page_source, 'lxml')
driver.close()
listupd = html.find_all('div', attrs={'class':"luf"})
if not listupd:
    print('no update')

luf = []
for upd in listupd:
    #prevent from error nonetype did not have li properties for chapter list
    print(upd.a)
    print(upd.ul.li)
    if not upd.a or not upd.ul.li:
        continue

    luf.append({
        'title': upd.a.get('title'),
        'name' : '',
        'url' : upd.a.get('href'),
        'chapter' : upd.ul.li.a.get_text().strip()
    })

print(luf)

