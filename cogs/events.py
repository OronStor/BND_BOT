# -*- coding: utf-8 -*-
from discord.ext import commands
import discord

ACTIVITY_IGNORE_LIST = [
    "Visual Studio Code"
]

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

        #Checking if its status update
        if after.status == discord.Status.online:
            #using main guild channel
            channel = after.guild.system_channel
            #define what status was before changing
            match before.status:
                case discord.Status.offline:
                    await channel.send(f"{after.mention} is online!")
                case discord.Status.idle:
                    await channel.send(f"{after.mention} is back!")
                case discord.Status.do_not_disturb:
                    await channel.send(f"{after.mention} isn`t busy now!")

        #checking if its activity update
        elif before.activity != after.activity and after.activity is not None and after.activity.name not in ACTIVITY_IGNORE_LIST:
            #using main guild channel
            channel = after.guild.system_channel
            await channel.send(f"{after.mention} ебашит в {after.activity.name}!")
            #if user , who changed activity in voice channel now
            if after.voice:
                #choose voice channel with current user
                voice_channel = after.voice.channel
                await channel.send(f"Можешь присоедениться к нему в {voice_channel.mention}")


#Load cog to bot
async def setup(bot):
    await bot.add_cog(EventsCog(bot))
