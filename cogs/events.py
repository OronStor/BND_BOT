from discord.ext import commands
import discord

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Welcome message for new member on server
    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"{member.mention} joined BND!")


    #Notification of changing members`s status offline/idle/busy -> online
    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if after.status == discord.Status.online:
            channel = after.guild.system_channel
            match before.status:
                case discord.Status.offline:
                    await channel.send(f"{after.mention} is online!")
                case discord.Status.idle:
                    await channel.send(f"{after.mention} is back!")
                case discord.Status.do_not_disturb:
                    await channel.send(f"{after.mention} isn`t busy now!")


#Load cog to bot
async def setup(bot):
    await bot.add_cog(EventsCog(bot))
