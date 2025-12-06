# -*- coding: utf-8 -*-
from discord.ext import commands
import discord
from data.guild.roles import roles
from data.guild.channels import channels
from data.guild.activity_blacklist import activity_blacklist

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

            #using game activity channel for notification
            channel_id = int(channels["game_activity"])
            channel = self.bot.get_channel(channel_id)

            #define what status was before changing
            match before.status:
                case discord.Status.offline:
                    await channel.send(f"{after.mention} is online!")
                case discord.Status.idle:
                    await channel.send(f"{after.mention} is back!")
                case discord.Status.do_not_disturb:
                    await channel.send(f"{after.mention} isn`t busy now!")


        if (
            before.activity != after.activity and #Activity changed
            after.activity is not None and        #User is doing smth (Quit a game is an activity for sm reason)
            after.activity.name not in ACTIVITY_IGNORE_LIST #Check activity for blacklist
        ):
            
            #using game activity channel for notific
            channel_id = int(channels["game_activity"])
            channel = self.bot.get_channel(channel_id)

            await channel.send(f"{after.mention} ебашит в {after.activity.name}!")

            #If user , who started activity in voice chat
            if after.voice:
                #Users voicechat
                voice_channel = after.voice.channel

                #If there is a role for this activity, we will invite everyone(with role) to voice
                role_to_mention = None
                for role, game in roles.items():
                    if game == after.activity.name:
                        role_to_mention = role
                        break
                
                #If we found role in data/roles
                if role_to_mention is not None:
                    await channel.send(f"<@&{role}>, заходите в {voice_channel.mention}")

                


#Load cog to bot
async def setup(bot):
    await bot.add_cog(EventsCog(bot))
