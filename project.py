import logging
import asyncio
import discord
from discord.ext import commands
from pathlib import Path

from config import settings

log = logging.getLogger("bot")

"""
Main function was rebuilded due to cs50 requirements
"""

def main():
    if not setup_logging():
        print("Failed to setup logging")
        return

    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        log.info("Bot interrupted by User")

async def start_bot():
    TOKEN = settings.discord_token
    
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.guild_messages = True
    intents.presences = True
    intents.voice_states = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        log.info(f"Logged in as {bot.user}")
        extensions = [
            "cogs.commands",
            "cogs.events",
            "cogs.notification",
            "cogs.gamble"
        ]
        for ext in extensions:
            try:
                await bot.load_extension(ext)
                log.info(f"Loaded extension: {ext}")
            except Exception as e:
                log.error(f"Failed to load extension {ext}: {e}")

    async with bot:
        await bot.start(TOKEN)

def setup_logging(level=logging.INFO):
    try:
        logging.basicConfig(
            level=level,
            format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        )
        return True
    except Exception:
        return False

def get_extension_paths(directory="cogs"):
    path = Path(directory)
    if not path.exists():
        return []
    return [f"{directory}.{f.stem}" for f in path.glob("*.py") if f.name != "__init__.py"]

def validate_config_exists(config_file="config.py"):
    return Path(config_file).is_file()

if __name__ == "__main__":
    main()