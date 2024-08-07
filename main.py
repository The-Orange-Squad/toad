import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from question_manager import QuestionManager
from ui_components import TruthDareView
from command_handlers import setup_commands
from database_manager import DatabaseManager
from submission_manager import SubmissionManager, setup_submission_commands
from help_command import setup_help_command

load_dotenv()
TOKEN = os.getenv('token')
MOD_CHANNEL_ID = int(os.getenv('modchannelid'))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

question_manager = QuestionManager()
db_manager = DatabaseManager()
submission_manager = SubmissionManager()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    await bot.change_presence(activity=discord.Game(name="Truth or Dare"))

setup_commands(bot, question_manager, db_manager)
setup_submission_commands(bot, submission_manager, question_manager)
setup_help_command(bot)

bot.run(TOKEN)