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
    sources = [
        _asura(web),
        _toonily(web),
        _mangareader(web)
    ]

    notification = []
    src = sources[0]
    anilist = await src.database.get_anilist(src.webname)
    update = await src.check_for_update()
    if not update:
        return notification
    
    new = await src.check_for_update_based_on_mangalist(anilist=anilist, manga = update)
    print(new)
    notification.append(update)
    manga_update = await src._get_manga_update_by_url(update[0].get('url'))
    for upd in update:
        title = upd.get('title')
        name = await src.clean_title(title)
        
        name_from_title = await src.generate_name_from_title(name)
        print(name_from_title)

    return notification

