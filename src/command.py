import discord
from discord.ext import commands
from manga import manga
import datetime as dt

from logs import logging
from config import colour
import string

class command(commands.Cog, manga):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
        self.log = logging(bot)
        self.startTime = dt.datetime.now() 
        self.connectionTime = dt.datetime.now()
    
    @commands.command()
    async def update(self, ctx):
        try:
            notification = await self._update()
        except Exception as error:
                return await self.log.error(error=error, title='bot', name='Update')
                
        if not notification:
            embed = discord.Embed(title='UPDATE', colour=colour.red)
            embed.add_field(name='Chapter', value='None', inline=False)

            return await ctx.send(embed=embed)

        for update in notification[::-1]:
            embed = discord.Embed(title=update.get('title'), colour=colour.blue)
            embed.add_field(name='Chapter', value=update.get('chapter'), inline=False)
            embed.add_field(name='URL', value=update.get('url'), inline=False)

            channel = await self.get_channel_id_by_name(name=await self.channel_name_from_title(update.get('title')))
            if not channel:
                channel = await self.create_channel_by_name(name=await self.channel_name_from_title(update.get('title')))

            await channel.send(embed=embed)
            await self.update_manga_database(update)
            await self.util.asyncio.sleep(1)

    @commands.command()
    async def uptime(self, ctx):
        upSeconds = dt.datetime.now() - self.startTime
        connSeconds = dt.datetime.now() - self.connectionTime
        
        embed = discord.Embed(title='[SERVER]', colour=colour.blue)
        embed.add_field(name='SERVER TIME', value=await self.util.uptime(upSeconds), inline=False)
        embed.add_field(name='BOT TIME', value=await self.util.uptime(connSeconds), inline=False)

        return await ctx.send(embed=embed)

    @commands.command()
    async def add(self, ctx, *name):
        if not name:
            embed = discord.Embed(title='ERROR', colour=colour.red)
            embed.add_field(name='command error', value='need manga name to add to list', inline=False)
            return await ctx.send(embed=embed)
        
        try:
            embed = await self._addmanga(" ".join(name))
        except Exception as error:
            return await self.log.error(error=error, title='bot', name='Add')

        channel = await self.get_channel_id_by_name(name = await self.channel_name_from_title(embed.title))
        if not channel:
            channel = await self.create_channel_by_name(name = await self.channel_name_from_title(embed.title))

        return await channel.send(embed=embed)

    @commands.command()
    async def search(self, ctx, *name):
        if not name:
            return False
        try:
            embed = await self._search(" ".join(name))
        except Exception as error:
            return await self.log.error(error=error, title='bot', name='Search')

        if not embed:
            embed = discord.Embed(title='ERROR', colour=colour.red)
            embed.add_field(name='command error', value='need manga name to add to list', inline=False)
            return await ctx.send(embed=embed)

        return await ctx.send(embed=embed)

    async def channel_name_from_title(self, title: str):
        return "-".join(title.strip(string.punctuation).split(' ')).lower()
