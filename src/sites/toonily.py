from bs4 import BeautifulSoup
from sites.sites import sites as manga

import json
import os

class toonily(manga):
    def __init__(self, scraper):
        super().__init__()
        self.scraper = scraper
        self.name = ['toonily', 'toonily.com', 'tnly']
        self.webname = self.name[1]
        self.manga = ""
        self.filename = 'toonily.json'

        self.url = "https://toonily.com/webtoon"
        self.searchurl = 'https://toonily.com/search'
        self.cookies = {'toonily-mature': 1}

        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            'Accept-Language': "en-US,en;q=0.9",
            'Accept-Encoding': "gzip, deflate, br",
            'sec-fetch-site': 'same-origin',
        }

    async def check_for_update(self):
        resp = await self.scraper.request('https://toonily.com', self.headers, cookies = self.cookies)
        if not resp:
            return False
        try:
            return await self.get_manga_chapter_update(resp)
        except Exception as error:
            await self._save_log(url=self.webname, code = 400, error = error)
            return False

    async def _parsehtml(self, resp):
        html = BeautifulSoup(resp, 'lxml')
        listupd = html.find_all('div', attrs={'class':"page-item-detail manga"})

        if not listupd:
            return False

        return listupd
    
    async def get_manga_chapter_update(self, resp):
        listupd = await self._parsehtml(resp)
        if not listupd:
            return False

        luf = []
        for upd in listupd:
            if not upd.div.a or not upd.find('div', attrs={'class': 'chapter-item'}):
                continue

            luf.append({
                'title': await self.generate_name_from_title(upd.div.a.get('title')),
                'name' : await self.parsetitlefromurl(upd.a.get('href')),
                'url' : f"{upd.a.get('href')}",
                'chapter' : upd.find('div', attrs={'class':'chapter-item'}).span.a.get_text().strip() if upd.find('div', attrs={'class': 'chapter-item'}) else None
            })
        
        return luf
    
    async def get_manga_search_result(self, resp):
        result = await self._parsehtml(resp)
        if not result:
            return False

        luf = []
        for res in result:
            if not res.find('div', attrs={'class': "item-summary"}):
                continue
            
            luf.append({
                'title': await self.generate_name_from_title(res.find('div', attrs={'class': "item-summary"}).div.h3.a.get_text().strip()),
                'name' : await self.parsetitlefromurl(res.find('div', attrs={'class': "item-summary"}).div.h3.a.get('href')),
                'url' : res.find('div', attrs={'class': "item-summary"}).div.h3.a.get('href'),
            })

        return luf

    async def _get_manga_update_by_url(self, url):
        if not url.startswith('https://'):
            return False

        update = await self.scraper.request(url, self.headers)
        if not update:
            return False

        return await self._parsechapterlist(update)

    async def _get_manga_update_by_name(self, manga):
        if manga.startswith('https://'):
            return False

        manga = f"{self.url}/{manga}/"
        self.manga = manga

        update = await self.scraper.request(manga, self.headers, self.cookies)
        if not update:
            return False

        return await self._parsechapterlist(update)

    async def _parsechapterlist(self, html):
        chapterlist = await self._chapterlist(data=html)
        if not chapterlist:
            return False

        return chapterlist

    async def search_by_url(self, url):
        resp = await self.scraper.request(url=url, headers=self.headers, cookies=self.cookies)
        if not resp:
            return False

        return await self._parsemangainfo(resp)

    async def search_by_name(self, name: str):
        search = "-".join(name.split(' '))
        resp = await self.scraper.request(url=f"{self.searchurl}/{search}", headers=self.headers, cookies=self.cookies)
        if not resp:
            return False
        
        #return only last 10 entry
        manga = await self.get_manga_search_result(resp)
        if not manga:
            return False
        
        return manga[:10]

    async def _parsemangainfo(self, data):
        bs = BeautifulSoup(data, 'lxml')
        html = bs.find('div', attrs={'class': 'tab-summary'})
        if not html:
            return False
        
        info = {
            'title': await self.generate_name_from_title(html.find('div', attrs={'class': 'post-title'}).get_text().strip()),
            'name': await self.parsetitlefromurl(html.find('div', attrs={'class': 'summary_image'}).a.get('href').strip()),
            'url': html.find('div', attrs={'class': 'summary_image'}).a.get('href').strip(),
            'synopsis': bs.find('div', attrs={'class': 'summary__content'}).get_text().strip(),
            'thumbnail': bs.find('div', attrs={'class':'summary_image'}).img.get('data-src').strip(),
            'chapters' : await self._chapterlist(bs) if bs.find('ul',attrs={"class":"main version-chap no-volumn"}) else await self._update(html.find('div', attrs={'class': 'summary_image'}).a.get('href').strip())
        }

        return info
    
    async def _chapterlist(self, data):
        if not isinstance(data, BeautifulSoup):
            bs = BeautifulSoup(data, 'lxml')
        else:
            bs = data

        html = bs.find('ul',attrs={"class":"main version-chap no-volumn"})
        if not html:
            return False
            
        chapters = html.find_all('li', attrs={'class':'wp-manga-chapter'}) 
        if not chapters:
            return False

        chptr = []
        for f in chapters:
            if not f.a:
                continue
            
            chptr.append({
                    'source' : self.webname,
                    "url": f.a.get('href'),
                    "chapter": 'Chapter ' + str(await self._get_chapter_num(f.a.get_text()))
            })
        
        return chptr