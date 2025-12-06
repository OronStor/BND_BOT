# -*- coding: utf-8 -*-
import discord
from discord.ext import commands

from config import settings

#Get bot token from env
TOKEN = settings.DISCORD_TOKEN

#Supported events
intents = discord.Intents.default()
intents.message_content = True  
intents.members = True
intents.guild_messages = True
intents.presences = True

#Creating an object of class Bot
bot = commands.Bot(command_prefix="!", intents=intents)

#Running on start
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    #Load cogs
    await bot.load_extension("cogs.commands")
    await bot.load_extension("cogs.events")
    await bot.load_extension("cogs.notification")
    await bot.load_extension("cogs.songs_player")

bot.run(TOKEN)
