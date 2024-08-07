import discord
import random
import discord.ui

class TruthDareView(discord.ui.View):
    def __init__(self, question_manager, max_rating):
        super().__init__()
        self.question_manager = question_manager
        self.max_rating = max_rating

    @discord.ui.button(label="Truth", style=discord.ButtonStyle.blurple)
    async def truth_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        question = self.question_manager.get_question('truth', self.max_rating)
        await self.send_question(interaction, question, 'TRUTH')

    @discord.ui.button(label="Dare", style=discord.ButtonStyle.red)
    async def dare_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        question = self.question_manager.get_question('dare', self.max_rating)
        await self.send_question(interaction, question, 'DARE')

    @discord.ui.button(label="Random", style=discord.ButtonStyle.grey)
    async def random_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        question = self.question_manager.get_random_question(self.max_rating)
        question_type = 'TRUTH' if question in self.question_manager.truths else 'DARE'
        await self.send_question(interaction, question, question_type)

    async def send_question(self, interaction: discord.Interaction, question, question_type):
        embed = discord.Embed(title=question['question'], color=discord.Color.blue())
        embed.set_footer(text=f"TYPE: {question_type} | RATING: {question['maxrating']} | ID: {question['ID']}")
        await interaction.response.edit_message(content=None, embed=embed, view=None)