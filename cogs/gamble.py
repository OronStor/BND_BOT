import random
import asyncio
from discord.ext import commands
import discord
from pathlib import Path
import json

BALANCE_FILE = Path('data/casino/user_balances.json')
PROBABILITY_FILE = Path('data/casino/slot_probabilities.json')
START_BALANCE = 1000

class GambleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.symbols, self.probabilities, self.multipliers = self.load_probabilities()

    #=========РЕГИСТРАЦИЯ И БАЛАНС===========

    # Функция для загрузки балансов из файла
    def load_balances(self):
        with open(BALANCE_FILE, 'r') as f:
            content = f.read().strip()
            return json.loads(content)  # Загружаем данные, если файл не пустой

    # Функция для сохранения балансов в файл
    def save_balances(self, balances):
        with open(BALANCE_FILE, 'w') as f:
            json.dump(balances, f, indent=4)

    @commands.command()
    async def register(self, ctx):
        user_id = str(ctx.author.id)
        user_balance = self.load_balances()

        if user_id in user_balance:
            balance = user_balance[user_id]
            await ctx.send(f"Вы уже зарегистрированы! Текущий баланс: {balance}💲")
        else:
            # Если пользователя нет, добавляем его с начальным балансом
            user_balance[user_id] = START_BALANCE
            self.save_balances(user_balance)
            await ctx.send(f"Поздравляем, {ctx.author}! Ваш стартовый баланс: {START_BALANCE}💲.")

    #===========СЛОТЫ============

    # Функция для загрузки данных о символах и их вероятности
    def load_probabilities(self):
        with open(PROBABILITY_FILE, 'r') as f:
            data = json.load(f)
            symbols = [item['symbol'] for item in data['symbols']]
            probabilities = [item['probability'] for item in data['symbols']]
            multipliers = data['multipliers']
            return symbols, probabilities, multipliers

    # Функция для получения символа с учетом вероятности
    def weighted_random(self):
        return random.choices(self.symbols, self.probabilities, k=1)[0]

    # Создание игрового поля (3x5)
    def generate_slot(self):
        return [
            [self.weighted_random() for _ in range(3)] for _ in range(3)
        ]

    # Проверка выигрышных линий
    def check_winning_lines(self, slot):
        winning_lines = []
        
        # Горизонтальные линии
        for row in slot:
            if len(set(row)) == 1:  # Все символы в линии одинаковые
                winning_lines.append(row)

        # Вертикальные линии
        for col in range(3):
            column = [slot[row][col] for row in range(3)]
            if len(set(column)) == 1:  # Все символы в колонке одинаковые
                winning_lines.append(column)

        # Диагонали
        diagonal1 = [slot[i][i] for i in range(3)]  # Левый верхний угол - правый нижний
        diagonal2 = [slot[i][2 - i] for i in range(3)]  # Правый верхний угол - левый нижний
        if len(set(diagonal1)) == 1:
            winning_lines.append(diagonal1)
        if len(set(diagonal2)) == 1:
            winning_lines.append(diagonal2)

        return winning_lines

    @commands.command()
    async def slots(self, ctx, bet: int):
        # Получаем баланс пользователя
        user_id = str(ctx.author.id)
        user_balance = self.load_balances()

        # Проверяем, достаточно ли средств для ставки
        if user_id not in user_balance:
            await ctx.send("Используйте команду `!register` для регистрации.")
            return

        balance = user_balance[user_id]

        if bet <= 0:
            await ctx.send(f"Самый умный что-ли? Иди нахуй")
            return

        if bet > balance:
            await ctx.send(f"Вы нищий! Ваш текущий баланс: {balance}💲")
            return

        # Имитация прокрутки
        slot_message = await ctx.send("🎰 Дэпчик...")
        for _ in range(3):  # Имитируем 3 прокруток
            slot = self.generate_slot()
            slot_display = "\n".join([" | ".join(row) for row in slot])
            await slot_message.edit(content=f"{slot_display}")  # Редактируем сообщение
            await asyncio.sleep(0.3)  # Задержка между прокрутками

        # После прокрутки генерируем итоговое поле
        final_slot = self.generate_slot()
        final_slot_display = "\n".join([" | ".join(row) for row in final_slot])
        winning_lines = self.check_winning_lines(final_slot)

        # Обновляем сообщение с итогом
        await slot_message.edit(content=f"{final_slot_display}\n")

        # Подсчёт выигрыша и изменение баланса
        if winning_lines:
            await ctx.send("Ты выиграл на комбинациях:")
            winnings = 0
            for line in winning_lines:
                print(line[0])
                multiplier = self.multipliers.get(line[0], 1)
                winnings += bet * multiplier
                await ctx.send(" | ".join(line))

            user_balance[user_id] += winnings
            await ctx.send(f"Вы выиграли {winnings}💲!")
            await ctx.send(f"Баланс = {user_balance[user_id]}💲")
        else:
            user_balance[user_id] -= bet
            await ctx.send(f"Вы проиграли {bet}💲")
            await ctx.send(f"Баланс = {user_balance[user_id]}💲")

        # Обновляем баланс
        self.save_balances(user_balance)

# Загружаем Cog в бота
async def setup(bot):
    await bot.add_cog(GambleCog(bot))
