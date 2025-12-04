from discord.ext import commands
import discord

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Welcome message for new member on server
    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"{member.mention} joined BND!")


    #Notification of changing members`s status offline -> online
    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if before.status == discord.Status.offline and after.status == discord.Status.online:
            #use main channel if it exists
            channel = after.guild.system_channel  
            if channel:
                await channel.send(f"{after.mention} is online now!")


#Load cog to bot
async def setup(bot):
    await bot.add_cog(EventsCog(bot))
