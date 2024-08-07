import discord
from discord.ext import commands
import csv
import random
import uuid
from collections import deque

class TruthDare(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.truths = self.load_csv('truths.csv')
        self.dares = self.load_csv('dares.csv')
        self.last_truths = deque(maxlen=5)
        self.last_dares = deque(maxlen=5)
        self.user_ratings = {}
        self.adult_role_ids = []  # Add adult role IDs here
        self.adult_channel_ids = []  # Add adult channel IDs here

    def load_csv(self, filename):
        data = []
        with open(filename, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not row['ID']:
                    row['ID'] = str(uuid.uuid4())
                data.append(row)
        
        # Save the updated CSV with IDs
        self.save_csv(filename, data)
        return data

    def save_csv(self, filename, data):
        with open(filename, 'w', newline='') as file:
            fieldnames = ['ID', 'question', 'maxrating']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    def get_question(self, question_type, user_id, channel_id, user_roles):
        questions = self.truths if question_type == 'truth' else self.dares
        user_rating = self.user_ratings.get(user_id, 0)
        
        eligible_questions = [
            q for q in questions 
            if int(q['maxrating']) <= user_rating and 
            q['ID'] not in (self.last_truths if question_type == 'truth' else self.last_dares)
        ]

        if user_rating >= 18 and (
            any(role.id in self.adult_role_ids for role in user_roles) and
            channel_id in self.adult_channel_ids
        ):
            eligible_questions.extend([q for q in questions if int(q['maxrating']) > 18])

        if not eligible_questions:
            return None

        question = random.choice(eligible_questions)
        if question_type == 'truth':
            self.last_truths.append(question['ID'])
        else:
            self.last_dares.append(question['ID'])

        return question

    @commands.slash_command(name="truth", description="Get a truth question")
    async def truth(self, ctx):
        await self.send_question(ctx, 'truth')

    @commands.slash_command(name="dare", description="Get a dare challenge")
    async def dare(self, ctx):
        await self.send_question(ctx, 'dare')

    @commands.slash_command(name="random", description="Get a random truth or dare")
    async def random_question(self, ctx):
        question_type = random.choice(['truth', 'dare'])
        await self.send_question(ctx, question_type)

    async def send_question(self, ctx, question_type):
        question = self.get_question(question_type, ctx.author.id, ctx.channel.id, ctx.author.roles)
        if not question:
            await ctx.respond("No suitable questions available. Try adjusting your rating or try again later.")
            return

        embed = discord.Embed(title=f"{question_type.capitalize()}", description=question['question'], color=discord.Color.blue())
        embed.set_footer(text=f"TYPE: {question_type.upper()} | RATING: {question['maxrating']} | ID: {question['ID']}")

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Truth", style=discord.ButtonStyle.blurple, custom_id="truth"))
        view.add_item(discord.ui.Button(label="Dare", style=discord.ButtonStyle.danger, custom_id="dare"))
        view.add_item(discord.ui.Button(label="Random", style=discord.ButtonStyle.secondary, custom_id="random"))

        await ctx.respond(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(TruthDare(bot))