import json
import asyncio
from datetime import datetime

import requests
import discord
from discord.ext import commands, tasks
from bs4 import BeautifulSoup

from config import settings

# Конфигурация
DISCORD_TOKEN = settings.DISCORD_TOKEN
CHANNEL_ID = 313685784169545728
STEAM_URL = (
    "https://store.steampowered.com/search/results/"
    "?query&start=0&count=100&dynamic_data=&sort_by=_ASC&specials=1&ndl=1"
    "&infinite=1&maxprice=free&json=1"
)
JSON_FILE = "free_games.json"


def load_previous_games() -> dict:
    """Загрузка предыдущего списка игр из JSON"""
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"games": [], "last_check": None}


def save_games(games_data: list[dict]) -> None:
    """Сохранение текущего списка игр в JSON"""
    data = {"games": games_data, "last_check": datetime.now().isoformat()}
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_html_games(html_content: str) -> list[dict]:
    """Парсинг HTML для извлечения игр со 100% скидкой"""
    soup = BeautifulSoup(html_content, "html.parser")
    games: list[dict] = []

    game_elements = soup.find_all("a", class_="search_result_row")
    for game in game_elements:
        try:
            discount_block = game.find("div", class_="discount_block")
            if not discount_block:
                continue

            discount = discount_block.get("data-discount")
            price_final = discount_block.get("data-price-final")

            # 100% скидка или финальная цена 0
            if discount == "100" or price_final == "0":
                app_id = game.get("data-ds-appid")

                title_element = game.find("span", class_="title")
                title = title_element.text.strip() if title_element else "Unknown"

                original_price_element = discount_block.find("div", class_="discount_original_price")
                original_price = original_price_element.text.strip() if original_price_element else "N/A"

                url = game.get("href", "")

                platforms = []
                platform_imgs = game.find_all("span", class_="platform_img")
                for platform in platform_imgs:
                    cls = platform.get("class", [])
                    if "win" in cls:
                        platforms.append("Windows")
                    if "mac" in cls:
                        platforms.append("Mac")
                    if "linux" in cls:
                        platforms.append("Linux")

                games.append(
                    {
                        "app_id": app_id,
                        "title": title,
                        "original_price": original_price,
                        "url": url,
                        "platforms": platforms,
                        "found_at": datetime.now().isoformat(),
                    }
                )
        except Exception as e:
            print(f"Ошибка при парсинге игры: {e}")
            continue

    return games


def fetch_free_games() -> list[dict]:
    """Получение списка бесплатных игр из Steam"""
    try:
        response = requests.get(STEAM_URL, timeout=30)
        response.raise_for_status()

        try:
            data = response.json()
            if data.get("success") == 1 and "results_html" in data:
                return parse_html_games(data["results_html"])
        except json.JSONDecodeError:
            return parse_html_games(response.text)

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к Steam: {e}")
        return []

    return []


def find_new_games(current_games: list[dict], previous_games: list[dict]) -> list[dict]:
    """Поиск новых игр со 100% скидкой"""
    previous_app_ids = {g.get("app_id") for g in previous_games}
    return [g for g in current_games if g.get("app_id") not in previous_app_ids]


def create_embed(game: dict) -> discord.Embed:
    """Создание Discord Embed для игры"""
    embed = discord.Embed(
        title=f"🎮 {game.get('title', 'Unknown')}",
        description="**Бесплатно!** (100% скидка)",
        color=0x00FF00,
        url=game.get("url", ""),
    )

    embed.add_field(name="💰 Обычная цена", value=game.get("original_price", "N/A"), inline=True)
    embed.add_field(name="🎯 Скидка", value="**100%**", inline=True)

    platforms = game.get("platforms") or []
    if platforms:
        embed.add_field(name="🖥️ Платформы", value=", ".join(platforms), inline=False)

    url = game.get("url", "")
    if url:
        embed.add_field(name="🔗 Ссылка", value=f"[Получить игру]({url})", inline=False)

    app_id = game.get("app_id")
    if app_id:
        embed.set_footer(text=f"App ID: {app_id}")

    found_at = game.get("found_at")
    if found_at:
        try:
            embed.timestamp = datetime.fromisoformat(found_at)
        except ValueError:
            pass

    return embed


class SteamFreeGamesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_id = CHANNEL_ID
        self.check_free_games.start()

    def cog_unload(self):
        self.check_free_games.cancel()

    async def _send_new_games(self, new_games: list[dict], current_games: list[dict]) -> None:
        channel = self.bot.get_channel(self.channel_id)
        if channel is None:
            # если бот еще не кешировал канал — попробуем fetch
            try:
                channel = await self.bot.fetch_channel(self.channel_id)
            except Exception:
                channel = None

        if channel is None:
            print(f"Канал с ID {self.channel_id} не найден")
            return

        for game in new_games:
            await channel.send(embed=create_embed(game))
            await asyncio.sleep(1)

        summary_message = (
            f"✨ **Найдено {len(new_games)} новых игр со 100% скидкой!**\n"
            f"Всего доступно: {len(current_games)} бесплатных игр"
        )
        await channel.send(summary_message)

    @tasks.loop(hours=1)
    async def check_free_games(self):
        """Проверка новых бесплатных игр каждый час"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Проверка бесплатных игр...")

        current_games = fetch_free_games()
        if not current_games:
            print("Не удалось получить список игр")
            return

        previous_data = load_previous_games()
        previous_games = previous_data.get("games", [])

        new_games = find_new_games(current_games, previous_games)
        if new_games:
            print(f"Найдено {len(new_games)} новых бесплатных игр!")
            await self._send_new_games(new_games, current_games)
        else:
            print("Новых бесплатных игр не обнаружено")

        save_games(current_games)
        print(f"Сохранено {len(current_games)} игр в {JSON_FILE}")

    @check_free_games.before_loop
    async def before_check_free_games(self):
        await self.bot.wait_until_ready()

    @commands.command(name="check")
    async def cmd_check(self, ctx: commands.Context):
        """Немедленная проверка бесплатных игр"""
        await ctx.send("🔍 Проверяю наличие бесплатных игр...")
        await self.check_free_games()  # ручной запуск тела loop
        await ctx.send("✅ Проверка завершена!")

    @commands.command(name="list")
    async def cmd_list(self, ctx: commands.Context):
        """Показать текущий список бесплатных игр"""
        data = load_previous_games()
        games = data.get("games", [])

        if not games:
            await ctx.send("📋 Список пуст. Используйте `!check` для проверки.")
            return

        await ctx.send(f"📋 **Текущий список бесплатных игр: {len(games)}**")
        for game in games[:10]:
            await ctx.send(embed=create_embed(game))

        if len(games) > 10:
            await ctx.send(f"... и еще {len(games) - 10} игр(ы)")

async def setup(bot: commands.Bot) -> None:
    """Register EventsCog in the bot."""
    await bot.add_cog(SteamFreeGamesCog(bot))
