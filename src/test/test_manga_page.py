#!bin/python

from scraper import scraper
from sites.asura import asura as _asura
from sites.toonily import toonily as _toonily
from sites.mangareader import mangareader as _mangareader

import string
async def name():
    return __name__

async def test_notification():
    web = scraper()
    toonily = _toonily(web)
    asura = _asura(web)
    mangareader = _mangareader(web)

    search_url = 'https://toonily.com/webtoon/solo-leveling-005/'
    result = await toonily.search_by_url(search_url)
    if not result:
        return False


    return result