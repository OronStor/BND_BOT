import logging

import discord
from discord.ext import commands

from data.guild.activity_blacklist import activity_blacklist
from data.guild.channels import channels
from data.guild.roles import roles

log = logging.getLogger(__name__)


class EventsCog(commands.Cog):
    """Server events: welcome messages, status and activity notifications."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Send a welcome log message when a member joins."""
        log.info("%s joined the server.", member)
      
    @commands.Cog.listener()
    async def on_presence_update(
        self,
        before: discord.Member,
        after: discord.Member,
    ) -> None:
        """
        Notify when:
        - Status switched to online;
        - Game activity changed and not in blacklist.
        Invite others when:
        -There is a role for this game
        -Player in voice chat
        """
        game_channel_id = int(channels["game_activity"])
        channel = self.bot.get_channel(game_channel_id)

        if channel is None:
            log.warning("Game activity channel with id %s not found.", game_channel_id)
            return

        # --- Status online ---
        if after.status == discord.Status.online:
            match before.status:
                case discord.Status.offline:
                    await channel.send(f"{after.mention} is online!")
                case discord.Status.idle:
                    await channel.send(f"{after.mention} is back!")
                case discord.Status.do_not_disturb:
                    await channel.send(f"{after.mention} isn’t busy now!")

        # --- Game activity ---
        if before.activity != after.activity and after.activity and after.activity.name.lower() not in [name.lower() for name in activity_blacklist]:
            if after.activity.type == discord.ActivityType.playing:
                await channel.send(f'{after.mention} теперь играет в {after.activity.name}')
            elif after.activity.type == discord.ActivityType.streaming:
                await channel.send(f'{after.mention} стримит: {after.activity.name}')
                
            if after.voice:
                log.info(after.voice)
                voice_channel = after.voice.channel

                role_to_mention = None
                for role_id, game_name in roles.items():
                    log.info(after.name.lower())
                    if game_name.lower() == after.activity.name.lower():
                        role_to_mention = role_id
                        log.info("НАШЕЛ")
                        break

                if role_to_mention is not None:
                    await channel.send(f"<@&{role_to_mention}>, заходите в {voice_channel.mention}")
                

async def setup(bot: commands.Bot) -> None:
    """Register EventsCog in the bot."""
    await bot.add_cog(EventsCog(bot))
