import logging
from logging import handlers
import os
import re

import discord
from discord.ext import commands


# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = handlers.TimedRotatingFileHandler('logs/hal.log', when='midnight', interval=1)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
handler.suffix = '%Y%m%d'
handler.extMatch = re.compile(r'^\d{8}$')
logger.addHandler(handler)

# Instantiation of the bot client
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)


# Events
@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))


@bot.event
async def on_message(message):
    if bot.user in message.mentions:
        await message.add_reaction('🍺')

    await bot.process_commands(message)


# Commands
@bot.command(aliases=['role'], description="Returns all your roles.")
async def roles(ctx):
    roles = [role.name for role in ctx.author.roles[1:]]
    roles = ', '.join(roles)
    await ctx.send(f"> {ctx.message.author.mention} - {roles}")


bot.run(os.getenv('HAL_DISCORD_TOKEN'))
