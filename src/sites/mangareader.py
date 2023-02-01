from bs4 import BeautifulSoup
from sites.sites import sites as manga
import json

class mangareader(manga):
    def __init__(self, scraper):
        super().__init__()
        self.scraper = scraper
        self.name = ['mangareader', 'mangareader.to', 'mr', 'mreader']
        self.webname = self.name[1]
        self.filename = 'mangareader.json'
        self.manga = ''
        
        self.url = 'https://mangareader.to'
        self.searchurl = 'https://mangareader.to/search?keyword'

        self.headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            'accept-language': "en-US,en;q=0.9",
            'accept-encoding': "gzip, deflate, br",
            'sec-fetch-site': 'same-origin'
        }

    async def check_for_update(self):
        resp = await self.scraper.request(url=f"{self.url}/home", headers=self.headers)
        if not resp:
            return False
        try:
            return await self._parsehtml(resp)
        except Exception as error:
            await self._save_log(url=self.webname, code = 400, error = error)
            return False

    async def _get_manga_update_by_url(self, url):
        if not url.startswith('https://'):
            return False

        update = await self.scraper.request(url, self.headers)
        if not update:
            return False

        return await self._parsechapterlist(update)

          
    async def _get_manga_update_by_name(self, manga):
        if not manga.startswith('https://'):
            manga = f"{self.url}/{manga}/"
            self.manga = manga
        else:
            mname = manga.split('/')
            self.manga = mname[-2]

        update = await self.scraper.request(manga, self.headers)
        if not update:
            return False

        return await self._parsechapterlist(update)
    
    async def _parsechapterlist(self, html):
        chapterlist = await self._chapterlist(data=html)
        if not chapterlist:
            return False

        return chapterlist

    async def search_by_url(self, url):
        resp = await self.scraper.request(url=url, headers=self.headers)
        if not resp:
            return False

        return await self._parsemangainfo(resp)

    async def search_by_name(self, name: str):
        search = "+".join(name.split(' '))
        resp = await self.scraper.request(url=f"{self.searchurl}={search}", headers=self.headers)
        if not resp:
            return False
        
        #return only last 10 entry
        manga = await self._parsehtml(resp)
        if not manga:
            return False
        
        return manga[:10]

    async def _parsehtml(self, resp):
        html = BeautifulSoup(resp, 'lxml')
        listupd = html.find_all('div', attrs={'class': 'item item-spc'})
        if not listupd:
            return False
        
        chapters = []
        for upd in listupd:
            if not upd.h3.a or not upd.find('div', attrs={'class':'fdl-item'}):
                continue

            chapters.append({
                'title' : await self.generate_name_from_title(upd.h3.a.get('title')),
                'name' : await self.parsetitlefromurl(upd.h3.a.get('href')),
                'chapter' : 'Chapter ' + str(await self._get_chapter_num(upd.find('div', attrs={'class':'fdl-item'}).find('div', attrs={'class':'chapter'}).a.get_text() if upd.find('div', attrs={'class':'fdl-item'}) else "")),
                'url' : self.url + upd.h3.a.get('href'),
            })

        return chapters
    
    async def _parsemangainfo(self, data):
        bs = BeautifulSoup(data, 'lxml')
        html = bs.find('div', attrs={'class': 'anisc-detail'})
        if not html:
            return False
        
        info = {
            'title': await self.generate_name_from_title(html.find('h2', attrs={'class': 'manga-name'}).get_text().strip()),
            'name': await self.parsetitlefromurl(self.url + html.find('div', attrs={'class': 'manga-buttons'}).a.get('href').strip()),
            'url': self.url + html.find('div', attrs={'class': 'manga-buttons'}).a.get('href').strip(),
            'synopsis': html.find('div', attrs={'class': 'sort-desc'}).find('div', attrs={'class': 'description'}).get_text().strip(),
            'thumbnail': bs.find('div', attrs={'class':'manga-poster'}).img.get('src').strip(),
            'chapters' : await self._chapterlist(bs)
        }

        return info
    
    async def _chapterlist(self, data):
        if not isinstance(data, BeautifulSoup):
            bs = BeautifulSoup(data, 'lxml')
        else:
            bs = data
            
        html = bs.find('div',attrs={"class":"chapters-list-ul"})
        if not html:
            return False
        
        chapters = html.find_all('li') 
        if not chapters:
            return False

        chptr = []
        for f in chapters:
            if not f.a: 
                continue
            
            chp = f.a.get('href')
            if 'en' in chp.split('/'):
                chptr.append({
                        'source' : self.webname,
                        "url": self.url + f.a.get('href'),
                        "chapter": f.a.get('title')[:f.a.get('title').rfind(':')].strip()
                })
        
        return chptr