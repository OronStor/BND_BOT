import logging
import random
from pathlib import Path

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class CommandsCog(commands.Cog):
    """Cog with simple fun commands like sending random images."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Load images from silvername folder
        self.silver_path = Path("data/silvername")
        self.silver_images = [
            file for file in self.silver_path.iterdir() if file.is_file()
        ]

        if not self.silver_images:
            log.warning("No images found in data/silvername/")

    @commands.command(name="feet")
    async def feet(self, ctx: commands.Context) -> None:
        """Asks user a weird question (fun)"""
        await ctx.send(
            f"Hey, {ctx.author.mention}... Can I smell your feet??"
        )

    @commands.command(name="silver")
    async def silver(self, ctx: commands.Context) -> None:
        """Send a random image from the silvername folder."""
        if not self.silver_images:
            await ctx.send("No images found in the silvername folder.")
            return

        selected_image = random.choice(self.silver_images)
        await ctx.send(file=discord.File(selected_image))


async def setup(bot: commands.Bot):
    """Register CommandsCog in the bot"""
    await bot.add_cog(CommandsCog(bot))

