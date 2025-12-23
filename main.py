import logging

import discord
from discord.ext import commands

from config import settings

TOKEN = settings.DISCORD_TOKEN
log = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)

# Supported events
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guild_messages = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    log.info(f"Logged in as {bot.user}")
    await bot.load_extension("cogs.commands")
    await bot.load_extension("cogs.events")
    await bot.load_extension("cogs.notification")
    await bot.load_extension("cogs.gamble")
    await bot.load_extension("cogs.steam_free_games")


bot.run(TOKEN)
