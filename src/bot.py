import discord
from discord.ext import commands

from config import discord as config 
from config import colour

from command import command
from task import task
from logs import logging 

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', description=config.description, intents=intents)
async def _log(embed):
    return await bot.get_channel(config.logchannel).send(embed=embed)

@bot.event
async def on_ready():
    await bot.add_cog(command(bot))
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name=" manga and mahwa update "
            )
        )
    embed = discord.Embed(title='[BOT]', colour=colour.green)
    embed.add_field(name='Status', value='Bot is online')
    await _log(embed=embed)

    _task.update.start()
    _task.errorlog.start()

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return 

    if isinstance(message.channel, discord.DMChannel):
        pass

@bot.event
async def on_command(ctx):
    if ctx.author == bot.user:
        return 

    if isinstance(ctx.channel, discord.DMChannel):
        return
    
    await ctx.message.delete(delay=0.5)

import asyncio
if __name__ == '__main__':
    _task = task(bot=bot)
    asyncio.get_event_loop().run_until_complete(bot.run(config.token))
    
