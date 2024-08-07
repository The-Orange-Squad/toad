import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import csv
import random
import uuid
from question_manager import QuestionManager
from ui_components import TruthDareView
from command_handlers import setup_commands
from database_manager import DatabaseManager

load_dotenv()
TOKEN = os.getenv('token')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

question_manager = QuestionManager()
db_manager = DatabaseManager()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    await bot.change_presence(activity=discord.Game(name="Truth or Dare"))

setup_commands(bot, question_manager, db_manager)

bot.run(TOKEN)