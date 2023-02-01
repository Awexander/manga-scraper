import json
import os
import jinja2
import asyncio
import random

from config import config   

class utils():
    def __init__(self):
        self.json = json
        self.os = os
        self.jinja = jinja2
        self.asyncio = asyncio
        self.random = random

    async def save(self, doc, data, dir=True):
        dirs = await self._checkfile(doc, dir)
        if doc.endswith(('.jpg', '.png')):
            with open(doc, 'wb') as wb:
                wb.write(data)
        
        else:
            with open(doc, 'w', encoding='utf-8') as w:
                if doc.endswith('.json'):
                    json.dump(data, w, indent=4, separators=[',', ':'])
                else:
                    w.write(str(data))

    async def read(self, doc, dir=True):
        dirs = await self._checkfile(doc,dir)
        if not dirs:
            return False
        
        with open(doc, 'r') as r:
            if doc.endswith('.json'):
                return json.loads(r.read())
            else:
                return r.read()
    
    async def append(self, doc, toappend, dir=True):
        r'''
        to append data to file and save it to directory

        parameters: 
        -----------
        doc : `str` 
            path to file
        toappend : `str` or `list` 
            data to append 
        dir : `bool`
            `True` to check if file exist or not 
            `False` to check if folder exist or not
        '''
        dirs = await self._checkfile(doc, dir)
        if not dirs:
            await self.save(doc, [])
        
        #read from json file
        fromfile = await self.read(doc)
        rw = []

        #appending list to new list
        if isinstance(toappend, list):
            _pdir = await self._readdir(doc)

            if _pdir.endswith('manga'):
                rw = await self._appendmanga(toappend=toappend, fromfile=fromfile)
            else:
                #append to new list to update the list
                rw = await self._appenddatabase(toappend, fromfile)
        

        #appending str to list
        if isinstance(toappend, str):
            #append to new list to update the list
            rw = await self._appendStr(toappend, fromfile)

        
        if not rw:
            return False
        
        #return new list
        return await self.save(doc, rw)
    
    async def _appendStr(self, toappend, fromfile):
        if toappend.lower() not in [f.lower() for f in fromfile]:
            fromfile.append(toappend)
        
        return fromfile

    async def _appendmanga(self, toappend, fromfile):
        for i, a in enumerate(toappend):
            if a.get('chapter') not in [f.get('chapter') for f in fromfile if a.get('title') == f.get('title')]:
                fromfile.append(a)
        
        return fromfile

    async def _appenddatabase(self, toappend, fromfile):
        for i, a in enumerate(toappend):
            #if manhwa is not in list or new chapter updated, append to new list
            #data = update, d = list from json file
            if a not in [f for f in fromfile]:
                if a.get('title') not in [f.get('title') for f in fromfile]:
                    #if manhwa not in list, use append 
                    fromfile.append(a)
                
                if a.get('chapter') not in [f.get('chapter') for f in fromfile if a.get('title') == f.get('title')]:
                    #find the entry with same title
                    entry = [f for f in fromfile if f.get('title') == a.get('title')]
                    #remove the already existed entry
                    #using for loop bcs entry is list, to avoid using index or index error
                    for e in entry:
                        fromfile.remove(e)
                    #insert data to the previous index of entry
                    fromfile.insert(i, a)

        return fromfile
    
    async def _readdir(self, doc):
        dirs = doc.split('/')
        if dirs[-1].endswith(('.json', '.html')):
            return dirs[-2]
        
        return dirs[-1]
    
    async def _checkfile(self, url, dir=True):
        files = url.split('/')

        if dir:
            #check if file existed in directory
            dirs = os.listdir("/".join(files[:-1]))
        else:
            #check if folder existed in directory
            dirs = os.listdir("/".join(files[:-2]))
            if files[-2] not in dirs:
                os.mkdir('/'.join(files[:-1]))

        #if file or folder not exist, return false
        if files[-1] not in os.listdir("/".join(files[:-1])):
            return False
        
        return True
    
    #create new directory 
    async def _mkdir(self, doc):
        files = doc.split('/')
        os.mkdir('/'.join(files[:-1]))
    
    async def uptime(self, time):
        minutes, seconds = divmod(time.total_seconds(), 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        upTime = []
        if days: 
            upTime.append('**{:01}** Days'.format(int(days)))
        if hours:
            upTime.append(' **{:02}** Hours'.format(int(hours)))
        if minutes:
            upTime.append(' **{:02}** Minutes'.format(int(minutes)))
        if seconds:
            upTime.append(' **{:02}** Seconds'.format(int(seconds)))

        return ':'.join(upTime)
