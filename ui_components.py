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
        await self.handle_button_click(interaction, 'truth')

    @discord.ui.button(label="Dare", style=discord.ButtonStyle.red)
    async def dare_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_button_click(interaction, 'dare')

    @discord.ui.button(label="Random", style=discord.ButtonStyle.grey)
    async def random_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_button_click(interaction, 'random')

    async def handle_button_click(self, interaction: discord.Interaction, question_type):
        # Remove buttons from the original message
        await interaction.message.edit(view=None)

        if question_type == 'random':
            question = self.question_manager.get_random_question(self.max_rating)
            question_type = 'TRUTH' if question in self.question_manager.truths else 'DARE'
        else:
            question = self.question_manager.get_question(question_type, self.max_rating)
            question_type = question_type.upper()

        embed = discord.Embed(title=question['question'], color=discord.Color.blue())
        embed.set_footer(text=f"TYPE: {question_type} | RATING: {question['maxrating']} | ID: {question['ID']}")

        # Create a new view for the new message
        new_view = TruthDareView(self.question_manager, self.max_rating)

        # Send a new message with the question and new view
        await interaction.response.send_message(embed=embed, view=new_view)