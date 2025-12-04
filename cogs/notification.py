from discord.ext import commands
import discord
import csv
from datetime import date
import math
from collections import OrderedDict

class NotificationCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    #Sends nearts birthdays to guild chat
    @commands.command()
    async def birthday(self,ctx):
        birthdays = {} #dict: "days_left":"user_id"
        nearest_birthdays = [] #list for searching nearest birthdays
        today = date.today() #getting date object

        with open("data/birthday.csv",mode = "r",newline = "",encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader) #skips csv header

            for row in reader:
                """
                csv file format:
                month, day, id
                "06", "10", "123123123123"
                """
                current_date = date.fromisoformat(f"{today.year}-{row[0]}-{row[1]}")

                #if birthday already was in this year -> find days_left to next
                if today > current_date:
                    current_date = current_date.replace(year = today.year + 1)

                time_delta = current_date - today
                days_left = abs(time_delta.days)
                
                nearest_birthdays.append(days_left)
                birthdays[str(days_left)] = row[2]

        #if you want to show more birthdays than we have in birthday.csv -> show all in birthday.csv
        amount_to_show = 3
        if amount_to_show > len(birthdays):
            amount_to_show = len(birthdays)
        
        #sorting list from the nearest to the latest
        nearest_birthdays = sorted(nearest_birthdays)

        for i in range(amount_to_show):
            days = nearest_birthdays[i]
            user_id = birthdays[str(days)]
            mention = f"<@{user_id}>"
            await ctx.send(f"{mention} - {days} days")
        






async def setup(bot):
    await bot.add_cog(NotificationCog(bot))