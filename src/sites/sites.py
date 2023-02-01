
from config import config
from utils import utils
from database.mangabase import mangabase

from unidecode import unidecode
import html
import json
import os
import re   
import string

class sites():
    def __init__(self):
        self.util = utils()
        self.database = mangabase()
        self.log_dir = 'log/log.json'
        self.percentage_match = 60

    async def update(self):
        anilist = await self.database.get_anilist(self.webname)
        if not anilist:
            return False
        try:
            listupd = await self.check_for_update()
            if not listupd:
                return False
        except Exception as error:
            await self._save_log(url=self.webname, code = 400, error = error)
            return False
        
        notification = []
        new = await self.check_for_update_based_on_mangalist(anilist=anilist, manga = listupd)
        # check if there is new update in listupd based on anilist
        # check with listupd list first to save memory usage? 
        # bcs listupd is latest update from website without filter favourites
        if new:
            #using for loop here to avoid list index error or if multiple entry in list
            #to iterate every new update
            #bcs sometimes, manhwa got bulk update, so need to always iterate each update
            for title in new:
                prevChapter = await self.database.get_manga_chapters(title.get('name'))
                if not prevChapter:
                    prevChapter = []

                if await self._get_chapter_num(title.get('chapter').strip()) in [chp.get('chapter') for chp in prevChapter]:
                    #skip updating if no new chapters or already updated (sent notification)
                    continue

                update = await self._get_manga_update_by_url(title.get('url'))
                if not update:
                    return False

                #there should not be 10 new chapters in one update right? 
                for n in update[:10]:
                    if await self._get_chapter_num(n.get('chapter')) not in [u.get('chapter') for u in prevChapter]:
                        n.update({
                            'title': title.get('title'),
                            'name' : title.get('name')
                            })
                        notification.append(n)

        return notification
    
    async def update_mange_chapters(self, update):
        return await self.database.update_manga_database(update)
        
    async def get_manga_info(self, url: str):
        if not url.startswith('https://'):
            return False

        info = await self.search_by_url(url)
        if not info:
            return False

        return info

    async def check_for_update_based_on_mangalist(self, anilist: list, manga: list):
        anilist_name = [f.get('name') for f in anilist]
        anilist_title = [f.get('title') for f in anilist]
        update_name = [f.get('name') for f in manga]
        update_title = [f.get('title') for f in manga]

        if [upd for upd in update_name if upd in anilist_name] or [upd for upd in update_title if upd in anilist_title]:
            new_update = [f for f in manga if f.get('name') in anilist_name or f.get('title') in anilist_title]
            for upd in new_update:
                if upd.get('name') not in anilist_name:
                    print("name not in database")
                    await self.database.update_manga_name(upd)

                if upd.get('title') not in anilist_title:
                    print("title not in database")
                    pass
                    await self.database.update_manga_title(upd)


            return new_update
        return []   

        for upd in manga:
            title = upd.get('title')
            match_list = [word in name.split('-') for word in title.split(' ')]
            matched = await self.calc_percentage_title_match(title=len([f for f in match_list if f is True]),
                                                             name=len(name.split('-'))
                                                            )

            if matched > self.percentage_match:
                new.append(upd)
        
        return new
    
    async def calc_percentage_title_match(self, title: int, name: int):
        return (title / name) * 100

    async def parsetitlefromurl(self, url):
        name = url.split('/')
        if not name[-1]:
            return name[-2]
        
        return name[-1]

    async def check_title_with_url(self, title: str, url: str) -> str:
        title = await self.clean_title(title)

    async def clean_title(self, title: str):
        title = html.unescape(title)
        title = unidecode(title)

        for a in title.split(' '):
            if len(a) <= 1:
                if a in string.punctuation:
                    title.replace(a, '')
        
        return re.sub(' +', ' ', title).lower()

    async def generate_name_from_title(self, title: str):
        title = await self.clean_title(title)
        punctuation = r"""!"#$%&'()*+,./:;<=>?@[\]^_`{|}~"""
        punctuation_table = str.maketrans("", "", punctuation)
        name_list = [f.translate(punctuation_table) for f in title.lower().split(" ")]

        return "-".join(name_list)

    async def _get_chapter_num(self, chapter:str):
        _num = ''
        for i, a in enumerate(chapter):
            if a.isnumeric() or a == '.':
                _num += a
                if i + 1 >= len(chapter):
                    continue

                if not chapter[i + 1].isnumeric():
                    if chapter[i + 1] == '.':
                        continue
                    break

        if not _num:
            return 0
        
        if '.' in _num:
            return float(_num)

        return int(_num)

    async def _save_log(self, url: str, code: int, error: str):
        return False
        data = []
        if os.path.exists(self.log_dir):
            with open(self.log_dir, 'r') as r:
                data = json.load(r)
        
        with open(self.log_dir, 'w') as w:
            data.append({
                            "url": url,
                            "code" : code,
                            "error" : error[:1023]
                        })

            json.dump(data, w, indent=4, separators=[',',':'])