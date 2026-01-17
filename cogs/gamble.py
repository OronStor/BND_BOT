from datetime import date
import random
import re
import logging
import asyncio
import json
from pathlib import Path

import discord
from discord.ext import commands

log = logging.getLogger(__name__)

BALANCE_FILE = Path("data/casino/user_balances.json")
PROBABILITY_FILE = Path("data/casino/slot_probabilities.json")
DAILY_FILE = Path("data/casino/daily.json")
START_BALANCE = 1000
DAILY_REWARD = 2000
SLOT_SIZE = 3
SPIN_COUNT = 3  # amount of spins before final
SPIN_DELAY = 0.3


class GambleCog(commands.Cog):
    """Cog with casino logics : registration and slot-machine"""

    def __init__(self, bot):
        self.bot = bot
        self.symbols, self.probabilities, self.multipliers = self.load_probabilities()
        self.active_player = None

    def load_balances(self) -> dict:
        """Load balances from json file to dict"""
        try:
            with open(BALANCE_FILE) as f:
                content = f.read().strip()
                return json.loads(content)
        except FileNotFoundError:
            log.warning("Error: File with users balances not found")
            return {}

    def save_balances(self, balances) -> None:
        """Save balances to json file"""
        with open(BALANCE_FILE, "w") as f:
            json.dump(balances, f, indent=4)

    def load_daily(self) -> dict:
        try:
            with open(DAILY_FILE) as f:
                content = f.read().strip()
                return json.loads(content)
        except FileNotFoundError:
            log.warning("Error: File with users daily not found")
            return {}

    def save_daily(self, daily) -> None:
        """Save date of last daily to file"""
        with open(DAILY_FILE, "w") as f:
            json.dump(daily, f, indent=4)

    @commands.command(name="balance")
    async def balance(self,ctx,mention: str=None) -> None:
        if mention is None:
            user_id = str(ctx.author.id)
        else:
            match = re.match(r'<@!?(\d+)>', mention)
            if match:
                user_id = match.group(1)
            else:
                await ctx.send("Error : can`t find user")
        balances = self.load_balances()
        guild = ctx.guild
        user = await guild.fetch_member(user_id)
        user_balance = balances[user_id]
        if user_balance is None:
            await ctx.send(f"{user.mention} is not registered!")
        else:
            await ctx.send(f"{user.mention} balance is {balances[user_id]}")

    @commands.command(name="register")
    async def register(self, ctx) -> None:
        """Add user data to balances json with start balance"""
        user_id = str(ctx.author.id)
        user_balance = self.load_balances()

        if user_id in user_balance:
            balance = user_balance[user_id]
            await ctx.send(f"You are already registered! Current balance : {balance}💲")
        else:
            user_balance[user_id] = START_BALANCE
            self.save_balances(user_balance)
            await ctx.send(
                f"Congrats, {ctx.author}! Your start balance: {START_BALANCE}💲."
            )

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx, amount_to_show: int = 5) -> None:
        """Shows users with biggest amount of tokens"""
        user_balances = self.load_balances()
        rating = sorted(user_balances.items(), key=lambda item: item[1], reverse=True)[
            :amount_to_show
        ]

        medals = ["🥇", "🥈", "🥉"]
        embed = discord.Embed(
            title="🏆 Best casino player:",
            description="Richest in BND:",
            color=discord.Color.gold(),
        )
        position = 0
        for player in rating:
            position += 1
            if position <= 3:
                place_marker = medals[position - 1]
            else:
                place_marker = f"#{position}"

            user_id = int(player[0])
            member = ctx.guild.get_member(user_id)
            balance = player[1]

            embed.add_field(
                name=f"{place_marker} {member.name}",
                value=f"{member.mention}\nБаланс: **{balance}💲**",
                inline=False,
            )
        top_user = ctx.guild.get_member(int(rating[0][0]))
        if top_user:
            embed.set_thumbnail(url=top_user.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.command(name="daily")
    async def daily(self, ctx):
        """Daily tokens once per day"""
        user_id = str(ctx.author.id)
        balances = self.load_balances()

        if user_id not in balances:
            await ctx.send("Use `!register` first to play!")
            return

        daily_claims = self.load_daily()
        today = date.today().isoformat()
        last_claim = daily_claims.get(user_id)

        if last_claim == today:
            await ctx.send("You have already claimed your daily")
            return

        balances[user_id] += DAILY_REWARD
        daily_claims[user_id] = today

        self.save_balances(balances)
        self.save_daily(daily_claims)

        await ctx.send(f"{ctx.author.mention} claimed {DAILY_REWARD}!")

    def load_probabilities(self) -> tuple[list[str], list[int], dict]:
        """Load symbols, probabilities, multipliers from json"""
        with open(PROBABILITY_FILE) as f:
            data = json.load(f)
            symbols = [item["symbol"] for item in data["symbols"]]
            probabilities = [item["probability"] for item in data["symbols"]]
            multipliers = data["multipliers"]
            return symbols, probabilities, multipliers

    def weighted_random(self) -> str:
        """Return a random symbol , depended on propabilities table"""
        return random.choices(self.symbols, self.probabilities, k=1)[0]

    def generate_slot(self) -> list[list[str]]:
        """Generate grid"""
        return [
            [self.weighted_random() for _ in range(SLOT_SIZE)] for _ in range(SLOT_SIZE)
        ]

    def check_winning_lines(self, slot) -> list[list[str]]:
        """Return a list with lines , where all symbols are the same"""
        winning_lines = []

        # Horizontal lines
        for row in slot:
            if len(set(row)) == 1:  # All symbols are same
                winning_lines.append(row)

        # Horizontal lines
        for col in range(3):
            column = [slot[row][col] for row in range(3)]
            if len(set(column)) == 1:  # All symbols are same
                winning_lines.append(column)

        # Diagonales
        diagonal1 = [slot[i][i] for i in range(3)]  # Top left - bottom right
        diagonal2 = [slot[i][2 - i] for i in range(3)]  # Top right - bottom left
        if len(set(diagonal1)) == 1:
            winning_lines.append(diagonal1)
        if len(set(diagonal2)) == 1:
            winning_lines.append(diagonal2)

        return winning_lines

    @commands.command(name="slots")
    async def slots(self, ctx, bet: int) -> None:
        """Play slots with specified bet"""

        # Check if someone playing now
        if self.active_player is not None:
            return

        self.active_player = True
        try:
            user_id = str(ctx.author.id)
            user_balance = self.load_balances()

            # Check if player didnt register
            if user_id not in user_balance:
                await ctx.send("Use command `!register` to start!.")
                return

            balance = user_balance[user_id]

            if bet <= 0:
                await ctx.send("Not enough tokens to play")
                return

            if bet > balance:
                await ctx.send(f"You are poor! Current balance: {balance}💲")
                return

            # Visualizing spin
            slot_message = await ctx.send("🎰 Rolling...")
            for _ in range(SPIN_COUNT):
                slot = self.generate_slot()
                slot_display = "\n".join([" | ".join(row) for row in slot])
                # Use message.edit to visualize spinning
                await slot_message.edit(content=f"{slot_display}")
                await asyncio.sleep(SPIN_DELAY)

            # Final grid
            final_slot = self.generate_slot()
            final_slot_display = "\n".join([" | ".join(row) for row in final_slot])
            winning_lines = self.check_winning_lines(final_slot)

            # Update final message
            await slot_message.edit(content=f"{final_slot_display}\n")

            # Calculate winning and edit balance
            result_lines: list[str] = []
            if winning_lines:
                result_lines.append("You won at lines:")
                winnings = 0
                for line in winning_lines:
                    symbol = line[0]
                    multiplier = self.multipliers.get(symbol, 1)
                    winnings += int(bet * multiplier)
                    result_lines.append(" | ".join(line))

                user_balance[user_id] += winnings
                result_lines.append(f"You won {winnings}💲!")
            else:
                user_balance[user_id] -= bet
                result_lines.append(f"You lost {bet}💲")

            result_lines.append(f"Balance = {user_balance[user_id]}💲")
            await ctx.send("\n".join(result_lines))
            self.save_balances(user_balance)
        finally:
            self.active_player = None


async def setup(bot):
    """Register GambleCog in the bot"""
    await bot.add_cog(GambleCog(bot))
