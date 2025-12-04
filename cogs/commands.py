from discord.ext import commands
import discord
import random
from pathlib import Path

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #get paths from silvername/
    silver_path = Path("data/silvername")
    silvername_pictures = [f for f in silver_path.iterdir() if f.is_file()]

    #Asks user to smell their feet
    @commands.command()
    async def feet(self, ctx):
        await ctx.send(f"Hey, {ctx.author.mention}... Can i smell your feet??")


    #Send random picture from data/silvername/
    @commands.command()
    async def silver(self, ctx):
        #Getting random number from 1 to number of files in data/silvername/
        ordinal_number = random.randint(1,len(self.silvername_pictures)-1)
        #Get path for picture with ordinal_number
        current_path = str(self.silvername_pictures[ordinal_number])
        print(current_path)
        await ctx.send(file=discord.File(current_path))


#Load cog to bot
async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
