import random
import logging
import asyncio
import json
from pathlib import Path

import discord
from discord.ext import commands

log = logging.getLogger(__name__)

BALANCE_FILE = Path('data/casino/user_balances.json')
PROBABILITY_FILE = Path('data/casino/slot_probabilities.json')
START_BALANCE = 1000
SLOT_SIZE = 3   #size of slot-machine
SPIN_COUNT = 3  #amount of spins before final
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
        with open(BALANCE_FILE, 'w') as f:
            json.dump(balances, f, indent=4)

    @commands.command(name="register")
    async def register(self, ctx) -> None:
        """Add user data to balances json with start balance"""        
        user_id = str(ctx.author.id)
        user_balance = self.load_balances()

        if user_id in user_balance:
            balance = user_balance[user_id]
            await ctx.send(
                f"You are already registered! Current balance : {balance}💲"
            )
        else:
            user_balance[user_id] = START_BALANCE
            self.save_balances(user_balance)
            await ctx.send(
                f"Congrats, {ctx.author}! Your start balance: {START_BALANCE}💲."
            )

    #===========СЛОТЫ============

    def load_probabilities(self) -> tuple[list[str], list[int], dict]:
        """Load symbols, probabilities, multipliers from json"""
        with open(PROBABILITY_FILE) as f:
            data = json.load(f)
            symbols = [item['symbol'] for item in data['symbols']]
            probabilities = [item['probability'] for item in data['symbols']]
            multipliers = data['multipliers']
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

    @commands.command(name = "slots")
    async def slots(self, ctx, bet: int) -> None:
        """Play slots with specified bet"""
        
        #Check if someone playing now
        if self.active_player is not None:
            return
        
        self.active_player = True
        try:
            user_id = str(ctx.author.id)
            user_balance = self.load_balances()

            # Проверяем, достаточно ли средств для ставки
            if user_id not in user_balance:
                await ctx.send("Use command `!register` to start!.")
                return

            balance = user_balance[user_id]

            if bet <= 0:
                await ctx.send(f"Not enough tokens to play")
                return

            if bet > balance:
                await ctx.send(f"You are poor! Current balance: {balance}💲")
                return

            # Visualizing spin
            slot_message = await ctx.send("🎰 Rolling...")
            for _ in range(SPIN_COUNT):
                slot = self.generate_slot()
                slot_display = "\n".join([" | ".join(row) for row in slot])
                #Use message.edit to visualize spinning
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
                    winnings += bet * multiplier
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
