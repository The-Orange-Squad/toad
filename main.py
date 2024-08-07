import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio

# Load environment variables
load_dotenv()
TOKEN = os.getenv('token')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Load cogs
async def load_extensions():
    await bot.load_extension("cogs.truth_dare")
    await bot.load_extension("cogs.settings")

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    await bot.change_presence(activity=discord.Game(name="Truth or Dare"))

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())