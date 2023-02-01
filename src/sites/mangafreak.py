from bs4 import BeautifulSoup
from sites.sites import sites as manga

class mangafreak(manga):
    def __init__(self):
        self.name = ['mf', 'mangafreak']
        self.webname = 'mangafreak.net'
        self.manga = ''
        self.filename = 'mangafreak.json'

        self.url = 'https://w14.mangafreak.net/'
        self.searchurl = 'https://w14.mangafreak.net/Search/'

        self.headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.3',
            'accept-language': 'en-US,en;q=0.9',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding' : 'gzip, deflate, br'
        }

    async def check_for_update(self):
        resp = self.scraper.request(self.url, self.headers)
        if not resp:
            return False

        html = BeautifulSoup(resp, 'lxml')
        listupd = html.find_all('div', attrs={'class': 'latest_item'})
        if not listupd: 
            return False

        mangas = []
        for upd in listupd:
            if not upd.a:
                continue

            chapters_list = upd.find('div', attrs={'class' : 'chapter_box'})
            mangas.append({
                'title' : upd.a.img.get('alt'),
                'name' : await self.parsetitlefromurl(upd.a.get('href')),
                'url' : upd.a.get('href'),
                'chapter' : [a.get('href') for a in chapters_list.find_all("a")]
            })

        return mangas