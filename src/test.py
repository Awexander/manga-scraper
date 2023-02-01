#!bin/python

import asyncio
import json
from test import (
    test_sites,
    test_manga_page,
    test_update_database
)

async def main():
    test_src = test_sites
    name = await test_src.name()
    #return_value = await test_sites.test_notification()
    return_value = await test_src.test_notification()
    
    await save_return(name=name, return_value=return_value)

async def save_return(name: str, return_value):
    if not return_value:
        return 

    name = f'data/test/{name}'
    if isinstance(return_value, dict) or isinstance(return_value, list):    
        with open(f'{name}.json', 'w', encoding='utf-8') as w:
            json.dump(return_value, w, indent=4, separators=[',',':'])

        return 

    with open(f'{name}.html', 'w', encoding='utf-8') as w:
        w.write(str(return_value))

asyncio.get_event_loop().run_until_complete(main())