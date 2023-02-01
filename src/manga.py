
import discord
from config import colour
from utils import utils

from scraper import scraper
from sites.asura import asura
from sites.toonily import toonily
from sites.mangareader import mangareader

import unidecode
import html
import string
import re
import os
import json
import contextlib
try:
    from urllib.parse import urlencode          
  
except ImportError:
    from urllib import urlencode
try:
    from urllib.request import urlopen
  
except ImportError:
    from urllib3 import urlopen


class manga:
    def __init__(self) -> None:
        self.util = utils()
        self.log_dir = 'log/log.json'
        self.scraper = scraper()
        self.sources = [
            toonily(self.scraper),
            asura(self.scraper),
            mangareader(self.scraper)
        ]
    
    async def _update(self):
        notification = []
        for src in self.sources:
            update = await src.update()
            if not update:
                continue

            for upd in update:
                notification.append(upd)

        return notification
    
    async def _search(self, name: str):
        url = re.search('^https?://([A-Za-z_0-9.-]+).*', name)
        if url:
            source_name = re.search('^https?://([A-Za-z_0-9.-]+).*', name)
            for src in  self.sources:
                #only search for manga info only when source is in link
                if source_name.group(1) in src.name:
                    manga = await src.get_manga_info(name)
                    if not manga:    
                        continue

                    return await self.embed_manga_info(manga)

        
        #if search without https:// link url 
        #search and return list of query search directly from website
        embed = discord.Embed(title=name, colour=colour.green)
        for src in  self.sources:
            manga = await src.search_by_name(name)
            if not manga:
                embed.add_field(name=src.name[0], value='empty', inline=False)
                continue

            for m in manga[:10]:
                value = f"{m.get('chapter')} \n {m.get('url')}"
                embed.add_field(name=m.get('title'), value=value, inline=False)
            
        return embed

    async def _addmanga(self, url: str):
        source_name = re.search('^https?://([A-Za-z_0-9.-]+).*', url)
        if source_name: 
            for src in self.sources:
            #get manga info from website
                if source_name.group(1) in src.name:
                    manga = await src.search_by_url(url)
                    if not manga:
                        embed = discord.Embed(title='Error adding manga')
                        embed.add_field(name='Error', value='No manga found in website', inline=False)

                        return embed

                    #adding manga to database
                    manga_details = []
                    for chapter in manga.get('chapters')[:10]:
                        manga_details.append({
                            'source' : chapter.get('source'),
                            'name' : manga.get('name'),
                            'url' : await self.tinyurl(chapter.get('url')),
                            'chapter' : await self.chapternum(chapter.get('chapter'))
                        })

                    await src.update_mange_chapters(manga_details)
                    return await self.embed_manga_info(manga)

    async def embed_manga_info(self, manga):
        embed = discord.Embed(title=manga.get('title'), colour=colour.green)
        embed.add_field(name='Title', value=manga.get('title'), inline=False)
        embed.add_field(name='Synopsis', value=manga.get('synopsis')[:1023], inline=False)
        embed.set_thumbnail(url=manga.get('thumbnail'))
        if manga.get('chapters'):
            for m in manga.get('chapters')[:5]:
                embed.add_field(name=m.get('chapter'), value=m.get('url'), inline=False)
            
        return embed

    async def get_channel_id_by_name(self, name):
        guild = discord.utils.get(self.bot.guilds, name='Testing and practice')
        cat = discord.utils.get(guild.categories, name = 'manga-update')
        return discord.utils.get(cat.text_channels, name=name)

    async def create_channel_by_name(self, name):
        guild = discord.utils.get(self.bot.guilds, name='Testing and practice')
        cat = discord.utils.get(guild.categories, name = 'manga-update')
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)  
        }

        return await guild.create_text_channel(name = name, category=cat, overwrites=overwrites)
    
    async def update_manga_database(self, update):
        for src in self.sources:
            if update.get('source') in src.name:
                await src.update_mange_chapters({
                    'source' : update.get('source'),
                    'name' : update.get('name'),
                    'title' : update.get('title'),
                    'url' : await self.tinyurl(update.get('url')),
                    'chapter' : await self.chapternum(update.get('chapter'))
                })

    async def chapternum(self, chapter:str):
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

    async def tinyurl(self, url):
        try:
            request_url = ('http://tinyurl.com/api-create.php?' + urlencode({'url':url}))
            with contextlib.closing(urlopen(request_url)) as response:                      
                resp =  response.read().decode('utf-8 ')
                return resp
        except:
            return False

    async def clean_title(self, title: str):
        title = html.unescape(title)
        title = unidecode(title)

        for a in title.split(' '):
            if len(a) <= 1:
                if a in string.punctuation:
                    title.replace(a, '')
        
        return re.sub(' +', ' ', title).lower()

    async def channel_name_from_title(self, title: str):
        title = await self.clean_title(title)
        punctuation = r"""!"#$%&'()*+,./:;<=>?@[\]^_`{|}~"""
        punctuation_table = str.maketrans("", "", punctuation)
        name_list = [f.translate(punctuation_table) for f in title.lower().split(" ")]

        return "-".join(name_list)

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
                            "error" : error
                        })

            json.dump(data, w, indent=4, separators=[',',':'])
