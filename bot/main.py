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


@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))

bot.run(os.getenv('HAL_DISCORD_TOKEN'))
