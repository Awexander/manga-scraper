import discord
from discord.ext import commands

from config import discord as config
from config import colour

import json
import os

class logging():
    def __init__(self, bot) -> None:
        self.bot = bot

    async def error(self, error: str, title: str='ERROR', name: str='error'):
        embed = discord.Embed(title=f'[{title.upper()}]', colour=colour.red)
        embed.add_field(name=f'{name.capitalize()}', value=error, inline=False)

        return await self.bot.get_channel(config.logchannel).send(embed=embed)

    async def log(self):
        if not os.path.exists('log/log.json'):
            return 

        with open('log/log.json', 'r') as r:
            error = json.loads(r.read())

            if not error:
                return 
                
        for err in error:
            embed = discord.Embed(title='Error', colour=colour.red)
            embed.add_field(name='Url', value=err.get('url'))
            embed.add_field(name='Code', value=err.get('code'))
            embed.add_field(name='Error', value=err.get('error')[:1023])

            await self.bot.get_channel(config.logchannel).send(embed=embed)

        os.remove('log/log.json')