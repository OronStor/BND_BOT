import logging
import json
from pathlib import Path

import discord
from discord.ext import commands

from data.guild.activity_blacklist import activity_blacklist
from data.guild.channels import channels

log = logging.getLogger(__name__)

USER_ACTIVITIES_PATH = Path('data/guild/user_activities.json')

def load_user_activities():
    if USER_ACTIVITIES_PATH.exists():
        try:
            with open(USER_ACTIVITIES_PATH, 'r') as f:
                return json.load(f)  
        except json.JSONDecodeError:
            log.error("Error decoding JSON in user_activities.json.")
            return {}  
    else:
        return {}  

def save_user_activities(user_activities):
    try:
        with open(USER_ACTIVITIES_PATH, 'w') as f:
            json.dump(user_activities, f, indent=4)  
            f.flush() 
        log.info("User activities saved to file.")
    except Exception as e:
        log.error(f"Error saving user activities: {e}")

class EventsCog(commands.Cog):
    """Server events: welcome messages, status and activity notifications."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.user_activities = load_user_activities()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Send a welcome log message when a member joins."""
        log.info("%s joined the server.", member)

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member) -> None:
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
        
        user_id = after.id

        # --- Status online ---
        if after.status == discord.Status.online:
            match before.status:
                case discord.Status.offline:
                    await channel.send(f"{after.mention} is online!")
                case discord.Status.idle:
                    await channel.send(f"{after.mention} is back!")
                case discord.Status.do_not_disturb:
                    await channel.send(f"{after.mention} isn’t busy now!")

        # --- Game activity blacklist ---
        if after.activity is not None and (after.activity.name.lower() not in [name.lower() for name in activity_blacklist]):
            if after.activity.type == discord.ActivityType.playing:
                
                current_activity = after.activity.name
                
                if user_id not in self.user_activities:
                    log.info("USER NOT IN HASH")
                    self.user_activities[user_id] = current_activity
                    await channel.send(f"{after.mention} is playing {current_activity} now!")
                    save_user_activities(self.user_activities)  
                    return
                else:
                    log.info("USER IN HASH")
                    last_activity = self.user_activities.get(user_id)
                    
                if current_activity != last_activity:
                    await channel.send(f"{after.mention} is playing {current_activity} now!")
                    self.user_activities[user_id] = current_activity
                    save_user_activities(self.user_activities)  
                    log.info(f"CHANGED to {current_activity}")
                else:
                    return

async def setup(bot: commands.Bot) -> None:
    """Register EventsCog in the bot."""
    await bot.add_cog(EventsCog(bot))
