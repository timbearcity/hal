import logging
from logging import handlers
import os
from random import randint
import re
import sqlite3

import discord
from discord.ext import commands
import wikipedia


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


# Connection to database
conn = sqlite3.connect('sqlite3.db')
c = conn.cursor()


# Events
@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))
    c.execute("SELECT userid FROM users")
    res = c.fetchall()
    for guild in bot.guilds:
        for member in guild.members:
            if member.id not in res:
                c.execute("INSERT INTO users(userid) VALUES(?)", (member.id,))
                conn.commit()


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


@bot.command(aliases=['wc'], description="Returns the requested Wikipedia article. If the keyword is followed by a number it will return another article that many random links deep from the origin article.")
async def wikiception(ctx, *args):
    args = list(args)
    depth = 0
    if args[-1].isdigit():
        depth = int(args.pop())
    title = wikipedia.search(' '.join(args), results=1, suggestion=False)[0]
    article = wikipedia.page(title=title, auto_suggest=False)
    results = [article.title]
    if depth > 0:
        for _ in range(depth):
            article = wikipedia.page(article.links[randint(0, len(article.links)-1)])
            results.append(article.title)
    await ctx.send(f"{' > '.join(results)}\n{article.url}")


bot.run(os.getenv('HAL_DISCORD_TOKEN'))
