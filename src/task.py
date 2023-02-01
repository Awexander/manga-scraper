
import discord
from discord.ext import tasks
import datetime as dt
import os
from config import colour
from manga import manga

from logs import logging

class task(manga):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
        self.log = logging(bot)
        self.updatetime = dt.datetime.now()

    @tasks.loop(seconds=5)
    async def update(self):
        delay = self.util.random.randrange(60, 120)
        if dt.datetime.now().timestamp() - self.updatetime.timestamp() >= delay:
            self.updatetime = dt.datetime.now()
            try:
                notification = await self._update()
            except Exception as error:
                return await self.log.error(error=error, title='bot', name='Update')
                
            if not notification:
                return False
                #await self.log.error(error=f"no update", title='bot', name='Update')
            
            for update in notification[::-1]:
                embed = discord.Embed(title=update.get('title'), colour=colour.green)
                embed.add_field(name='Chapter', value=update.get('chapter'), inline=False)
                embed.add_field(name='URL', value=update.get('url'), inline=False)

                channel = await self.get_channel_id_by_name(name = await self.channel_name_from_title(update.get('title')))
                if not channel:
                    await self.log.error(error=f"creating channel for {update.get('title')}", title='log')
                    channel = await self.create_channel_by_name(name = await self.channel_name_from_title(update.get('title')))

                await channel.send(embed=embed)
                await self.update_manga_database(update)
                await self.util.asyncio.sleep(1)
    
    @tasks.loop(seconds=5)
    async def errorlog(self):
        try:
            return await self.log.log()
        except Exception as error:
            os.remove('log/log.json')
            return await self.log.error(error=error)
