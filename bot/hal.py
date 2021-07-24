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


# CREATE TABLE members(id INTEGER PRIMARY KEY, userid INTEGER NOT NULL, guildid INTEGER NOT NULL, experience INTEGER DEFAULT 0, currency INTEGER DEFAULT 0);
# Connection to database
conn = sqlite3.connect('sqlite3.db')
c = conn.cursor()


# Events
@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))
    c.execute("SELECT userid, guildid FROM members")
    res = c.fetchall()
    for guild in bot.guilds:
        for member in guild.members:
            if (member.id, guild.id) not in res and not member.bot:
                c.execute("INSERT INTO members(userid, guildid) VALUES(?,?)", (member.id, guild.id))
                conn.commit()


# Experience system
def get_level(exp):
    if exp < 50:
        return 1
    elif exp < 100:
        return 2
    elif exp < 200:
        return 3
    elif exp < 300:
        return 4
    elif exp < 400:
        return 5
    elif exp < 500:
        return 6
    elif exp < 1000:
        return 7
    elif exp < 3000:
        return 8
    elif exp < 5000:
        return 9
    elif exp < 10000:
        return 10


@bot.event
async def on_message(message):
    """Members get 1 experience point per message they send."""
    if not message.author.bot:
        c.execute("UPDATE members SET experience = experience + 1 WHERE userid = ?", (message.author.id,))
        conn.commit()
    await bot.process_commands(message)


@bot.command(aliases=['experience', 'exp', 'xp'], description="Returns your current level and experience points.")
async def level(ctx):
    c.execute("SELECT experience FROM members WHERE userid = ? AND guildid = ?", (ctx.author.id, ctx.guild.id))
    exp = c.fetchone()[0]
    lvl = get_level(exp)
    await ctx.send(f"{ctx.author.mention}\nLevel: {lvl}\nExperience: {exp}")


# Miscellaneous commands
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
            article = wikipedia.page(title=article.links[randint(0, len(article.links)-1)], auto_suggest=False)
            results.append(article.title)
    await ctx.send(f"{' > '.join(results)}\n{article.url}")


bot.run(os.getenv('HAL_DISCORD_TOKEN'))
