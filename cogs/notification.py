import csv
from datetime import date
from pathlib import Path

import discord
from discord.ext import commands

BIRTHDAY_FILE = Path("data/guild/birthday.csv")


class NotificationCog(commands.Cog):
    """
    Commands related to notifications and dates.
    """

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="birthday")
    async def birthday(
        self,
        ctx: commands.Context,
        amount_to_show: int = 3,
    ) -> None:
        """
        Shows nearest birthdays of guild members

        CSV format:
        month, day, user_id
        """

        if not BIRTHDAY_FILE.exists():
            await ctx.send("Birthday file not found.")
            return

        birthdays = {}  # "days_left":"user_id"
        nearest_birthdays = []
        today = date.today()

        with BIRTHDAY_FILE.open(
            mode="r",
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.reader(file)
            header = next(reader)  # skip header

            for row in reader:
                current_date = date.fromisoformat(f"{today.year}-{row[0]}-{row[1]}")

                # if birthday already was in this year -> search in next year
                if today > current_date:
                    current_date = current_date.replace(year=today.year + 1)

                time_delta = current_date - today
                days_left = abs(time_delta.days)

                nearest_birthdays.append(days_left)
                birthdays[str(days_left)] = row[2]

        # if you want to show more than we have in file -> show all in file
        if amount_to_show > len(birthdays):
            amount_to_show = len(birthdays)

        nearest_birthdays = sorted(nearest_birthdays)
        result_lines = []
        for i in range(amount_to_show):
            days = nearest_birthdays[i]
            user_id = birthdays[str(days)]
            mention = f"<@{user_id}>"
            result_lines.append(f"{mention} - {days} days")

        await ctx.send("\n".join(result_lines))


async def setup(bot) -> None:
    """Register NotificationCog in the bot"""
    await bot.add_cog(NotificationCog(bot))
