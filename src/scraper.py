import aiohttp
from discord import Embed

from config import config, colour
from utils import utils

import json
import os
import functools
import typing
import asyncio
from selenium import webdriver

from selenium.webdriver.firefox.options import Options as firefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

class scraper():
    def __init__(self):
        self.client = aiohttp
        self.util = utils()
        self.log_dir = 'log/log.json'

    def to_thread(func: typing.Callable) -> typing.Coroutine:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await asyncio.to_thread(func, *args, **kwargs)
        return wrapper

    async def request(self, url, headers = {}, cookies={}):
        if not headers:
            headers = await self._headers()
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(30)) as session:
            async with session.get(url=url, headers=headers, cookies=cookies) as response:
                if response.status == 200:
                    return await response.text()

                return await self.firefox(url)
    
    async def firefox(self, url):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        options.add_argument('--connect-existing')
        # Instantiate a remote WebDriver
        try:
            self.driver = webdriver.Remote(
            command_executor='http://0.0.0.0:4444',
            options=options
            )
        except:
            self.driver.quit()
            self.driver = webdriver.Remote(
                command_executor='http://0.0.0.0:4444',
                options=options
            )
        self.driver.get(url=url)
        response = self.driver.page_source   
        self.driver.delete_all_cookies()
        self.driver.quit()
        return response

    async def get(self, url, headers= {}, cookies = {}):
        if not headers:
            headers = await self._headers()

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(30)) as session:
            async with session.get(url, headers=headers, cookies=cookies) as response:
                if response.status == 200:
                    resp = await response.read()
                    return resp
                else:
                    return False

    async def _headers(self):
        return await self.util.read(config.headersdir)
         
    async def _save_log(self, url: str, code: int, error: str):
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
