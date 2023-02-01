
from bs4 import BeautifulSoup
from sites.sites import sites as manga

class asura(manga):
    def __init__(self, scraper):
        super().__init__()
        self.scraper = scraper
        self.name = ['asura', 'asura.gg']
        self.webname = self.name[1]
        self.manga = ''
        self.filename = 'asura.json'

        self.url = 'https://www.asurascans.com/manga'
        self.searchurl = 'https://www.asurascans.com/?s'

        self.headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.3',
            'accept-language': 'en-US,en;q=0.9',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'sec-fetch-mode': 'navigate',
        }
    
    async def check_for_update(self):
        resp = await self.scraper.request('https://www.asurascans.com/', self.headers)
        if not resp:
            return await self._save_log(url=self.webname, code = 400, error = f'Error requesting for {self.webname}')
        
        html = BeautifulSoup(str(resp), 'html.parser')
        listupd = html.find_all('div', attrs={'class':"luf"})
        if not listupd:
            return False

        luf = []
        for upd in listupd:
            #prevent from error nonetype did not have li properties for chapter list
            if not upd.a or not upd.ul.li: 
                continue

            luf.append({
                'title': await self.generate_name_from_title(upd.a.get('title')),
                'name' : await self.parsetitlefromurl(upd.a.get('href')),
                'url' : upd.a.get('href'),
                'chapter' : upd.ul.li.a.get_text().strip()
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

        return await self._parsemangainfo(url, resp)

    async def search_by_name(self, name: str):
        url = "+".join(name.split(' '))
        resp = await self.scraper.request(url=f"{self.searchurl}={url}", headers=self.headers)
        if not resp:
            return False

        html = BeautifulSoup(resp, 'lxml')
        listupd = html.find_all('div', attrs={'class':"bsx"})
        if not listupd:
            return False

        luf = []
        for upd in listupd:
            if not upd.a or not upd.find('div', attrs={'class': 'epxs'}):
                continue

            luf.append({
                'title': await self.generate_name_from_title(upd.a.get('title')),
                'name' : await self.parsetitlefromurl(upd.a.get('href')),
                'url' : f"{upd.a.get('href')}",
                'chapter' : upd.find('div', attrs={'class': 'epxs'}).get_text()
            })
        
        if not luf:
            return False
        
        return luf[:10]

    async def _parsemangainfo(self, url, data):
        bs = BeautifulSoup(data, 'lxml')
        html = bs.find('div', attrs={'class': 'infox'})
        if not html:
            return False
        
        info = {
            'title': await self.generate_name_from_title(html.find('h1', attrs={'class': 'entry-title'}).get_text().strip()),
            'name' : await self.parsetitlefromurl(url),
            'url' : url,
            'synopsis': " ".join([p.get_text() for p in html.find('div', attrs={
                'class':'entry-content entry-content-single', 
                'itemprop':"description"}).find_all('p')]).strip() if html.find('div', attrs={
                'class':'entry-content entry-content-single', 
                'itemprop':"description"}) else None,
            'thumbnail': bs.find('div', attrs={'class':'thumb'}).img.get('data-cfsrc') if bs.find('div', attrs={'class':'thumb'}) else None,
            'chapters' : await self._chapterlist(bs) if bs.find('div',attrs={"id":"chapterlist"}) else await self._update(html.find('div', attrs={'class': 'bsx'}).a.get('href').strip() if html.find('div', attrs={'class': 'bsx'}) else None)
        }
        
        return info
        
    async def _chapterlist(self, data):
        if not isinstance(data, BeautifulSoup):
            bs = BeautifulSoup(data, 'lxml')
        else:
            bs = data

        html = bs.find('div',attrs={"id":"chapterlist"})
        if not html:
            return False
        
        chapters = html.find_all('li') 
        if not chapters:
            return False
        
        chptr = []
        for f in chapters:
            if not f.div.div.a:
                continue

            chptr.append({
                    'source' : self.webname,
                    "url": f.div.div.a.get('href'),
                    "chapter": 'Chapter ' + str(await self._get_chapter_num(f.div.div.a.find('span', attrs={'class':'chapternum'}).get_text().strip()))
            })
        
        return chptr