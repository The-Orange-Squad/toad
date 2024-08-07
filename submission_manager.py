import sqlite3
import random
from discord.ext import commands
import discord
from discord.commands import Option

class SubmissionManager:
    def __init__(self, db_name='submissions.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                question TEXT,
                question_type TEXT,
                maxrating INTEGER,
                status TEXT
            )
        ''')
        self.conn.commit()

    def submit_question(self, user_id, question, question_type, maxrating):
        self.cursor.execute('''
            INSERT INTO submissions (user_id, question, question_type, maxrating, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, question, question_type, maxrating, 'awaiting approval'))
        self.conn.commit()

    def get_random_unreviewed_question(self):
        self.cursor.execute('SELECT * FROM submissions WHERE status = "awaiting approval" ORDER BY RANDOM() LIMIT 1')
        return self.cursor.fetchone()

    def update_question_status(self, question_id, new_status):
        self.cursor.execute('UPDATE submissions SET status = ? WHERE id = ?', (new_status, question_id))
        self.conn.commit()

    def get_user_questions(self, user_id, offset, limit):
        self.cursor.execute('SELECT * FROM submissions WHERE user_id = ? LIMIT ? OFFSET ?', (user_id, limit, offset))
        return self.cursor.fetchall()

    def get_question_count(self, user_id):
        self.cursor.execute('SELECT COUNT(*) FROM submissions WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def delete_question(self, question_id, user_id):
        self.cursor.execute('DELETE FROM submissions WHERE id = ? AND user_id = ?', (question_id, user_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def edit_question(self, question_id, user_id, new_question, new_type, new_maxrating):
        self.cursor.execute('''
            UPDATE submissions 
            SET question = ?, question_type = ?, maxrating = ?, status = "awaiting approval"
            WHERE id = ? AND user_id = ?
        ''', (new_question, new_type, new_maxrating, question_id, user_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

def setup_submission_commands(bot, submission_manager, question_manager):
    @bot.slash_command(name="submit", description="Submit a new truth or dare question")
    async def submit(ctx, question: str, question_type: Option(str, description="Type of question (TRUTH or DARE"), maxrating: Option(int, description="Maximum rating for the question (1-18)")):
        if question_type not in ['TRUTH', 'DARE']:
            await ctx.respond("Question type must be either TRUTH or DARE", ephemeral=True)
            return
        if maxrating < 1 or maxrating > 18:
            await ctx.respond("Max rating must be between 1 and 18", ephemeral=True)
            return
        
        submission_manager.submit_question(ctx.author.id, question, question_type, maxrating)
        await ctx.respond("Your question has been submitted for review!", ephemeral=True)

    @bot.slash_command(name="review", description="Review submitted questions")
    @commands.has_permissions(manage_roles=True)
    async def review(ctx):
        question = submission_manager.get_random_unreviewed_question()
        if not question:
            await ctx.respond("No questions to review at this time.", ephemeral=True)
            return

        embed = discord.Embed(title="Question Review", description=question[2], color=discord.Color.blue())
        embed.add_field(name="Type", value=question[3])
        embed.add_field(name="Max Rating", value=question[4])
        
        view = ReviewView(bot, submission_manager, question_manager, question[0])
        await ctx.respond(embed=embed, view=view, ephemeral=True)

    @bot.slash_command(name="check_questions", description="View your submitted questions")
    async def check_questions(ctx):
        page = 0
        view = QuestionPaginatorView(submission_manager, ctx.author.id, page)
        await view.update_message(ctx)

    @bot.slash_command(name="delete_question", description="Delete one of your submitted questions")
    async def delete_question(ctx, question_id: int):
        if submission_manager.delete_question(question_id, ctx.author.id):
            await ctx.respond("Question deleted successfully!", ephemeral=True)
        else:
            await ctx.respond("Failed to delete question. Make sure you're the author and the ID is correct.", ephemeral=True)

    @bot.slash_command(name="edit_question", description="Edit one of your submitted questions")
    async def edit_question(ctx, question_id: int, new_question: str, new_type: str, new_maxrating: int):
        if new_type not in ['TRUTH', 'DARE']:
            await ctx.respond("Question type must be either TRUTH or DARE", ephemeral=True)
            return
        if new_maxrating < 1 or new_maxrating > 18:
            await ctx.respond("Max rating must be between 1 and 18", ephemeral=True)
            return
        
        if submission_manager.edit_question(question_id, ctx.author.id, new_question, new_type, new_maxrating):
            await ctx.respond("Question edited successfully! It will be reviewed again.", ephemeral=True)
        else:
            await ctx.respond("Failed to edit question. Make sure you're the author and the ID is correct.", ephemeral=True)

class ReviewView(discord.ui.View):
    def __init__(self, bot, submission_manager, question_manager, question_id):
        super().__init__()
        self.bot = bot
        self.submission_manager = submission_manager
        self.question_manager = question_manager
        self.question_id = question_id

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, button: discord.ui.Button, interaction: discord.Interaction):
        question = self.submission_manager.get_random_unreviewed_question()
        self.submission_manager.update_question_status(self.question_id, 'approved')
        
        # Add the question to the appropriate file
        if question[3] == 'TRUTH':
            self.question_manager.truths.append({
                'ID': str(question[0]),
                'question': question[2],
                'maxrating': str(question[4])
            })
            self.question_manager.save_csv('truths.csv', self.question_manager.truths)
        else:
            self.question_manager.dares.append({
                'ID': str(question[0]),
                'question': question[2],
                'maxrating': str(question[4])
            })
            self.question_manager.save_csv('dares.csv', self.question_manager.dares)

        await interaction.response.send_message("Question approved and added to the database.", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.submission_manager.update_question_status(self.question_id, 'rejected')
        await interaction.response.send_message("Question rejected.", ephemeral=True)
        self.stop()

class QuestionPaginatorView(discord.ui.View):
    def __init__(self, submission_manager, user_id, page):
        super().__init__()
        self.submission_manager = submission_manager
        self.user_id = user_id
        self.page = page

    async def update_message(self, ctx):
        offset = self.page * 5
        questions = self.submission_manager.get_user_questions(self.user_id, offset, 5)
        total_questions = self.submission_manager.get_question_count(self.user_id)

        embed = discord.Embed(title="Your Submitted Questions", color=discord.Color.blue())
        for q in questions:
            embed.add_field(name=f"ID: {q[0]} - {q[3]} (Max Rating: {q[4]})", value=f"Q: {q[2]}\nStatus: {q[5]}", inline=False)

        embed.set_footer(text=f"Page {self.page + 1}/{(total_questions - 1) // 5 + 1}")

        if isinstance(ctx, discord.Interaction):
            await ctx.response.edit_message(embed=embed, view=self)
        else:
            await ctx.respond(embed=embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.grey)
    async def previous(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.page = max(0, self.page - 1)
        await self.update_message(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.grey)
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        total_questions = self.submission_manager.get_question_count(self.user_id)
        self.page = min((total_questions - 1) // 5, self.page + 1)
        await self.update_message(interaction)