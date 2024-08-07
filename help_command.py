import discord
from discord import SelectOption

class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.current_page = 0
        self.pages = [
            {
                "title": "TOAD - Truth or Dare Bot",
                "description": "Welcome to the TOAD help menu! Use the dropdown to navigate through different sections.",
                "fields": [
                    {"name": "About TOAD", "value": "TOAD is a fun Truth or Dare bot for Discord. Enjoy playing with your friends!"},
                    {"name": "How to Use", "value": "Select a category from the dropdown menu below to see more information about specific commands and features."}
                ]
            },
            {
                "title": "Basic Commands",
                "description": "Here are the main commands you can use with TOAD:",
                "fields": [
                    {"name": "/truth", "value": "Get a random truth question"},
                    {"name": "/dare", "value": "Get a random dare challenge"},
                    {"name": "/random", "value": "Get either a truth or dare randomly"}
                ]
            },
            {
                "title": "Rating System",
                "description": "TOAD uses a rating system to ensure age-appropriate content:",
                "fields": [
                    {"name": "/set_rating", "value": "Set your preferred maximum rating (1-18)"},
                    {"name": "/view_rating", "value": "View your current maximum rating"}
                ]
            },
            {
                "title": "Submission System",
                "description": "TOAD allows users to submit their own questions:",
                "fields": [
                    {"name": "/submit", "value": "Submit a new truth or dare question"},
                    {"name": "/check_questions", "value": "View your submitted questions"},
                    {"name": "/delete_question", "value": "Delete one of your submitted questions"},
                    {"name": "/edit_question", "value": "Edit one of your submitted questions"}
                ]
            },
            {
                "title": "Moderator Commands",
                "description": "These commands are only available to users with manage roles permission:",
                "fields": [
                    {"name": "/review", "value": "Review submitted questions"}
                ]
            }
        ]

        # Add the select menu to the view
        self.add_item(PageSelect(self.pages))

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.grey)
    async def previous_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = (self.current_page - 1) % len(self.pages)
        await self.update_message(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.grey)
    async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = (self.current_page + 1) % len(self.pages)
        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        page = self.pages[self.current_page]
        embed = discord.Embed(title=page["title"], description=page["description"], color=discord.Color.blue())
        for field in page["fields"]:
            embed.add_field(name=field["name"], value=field["value"], inline=False)
        await interaction.response.edit_message(embed=embed, view=self)

class PageSelect(discord.ui.Select):
    def __init__(self, pages):
        options = [
            SelectOption(label=page["title"], description=page["description"][:100], value=str(i))
            for i, page in enumerate(pages)
        ]
        super().__init__(placeholder="Choose a category...", options=options)

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        view.current_page = int(self.values[0])
        await view.update_message(interaction)

def setup_help_command(bot):
    @bot.slash_command(name="help", description="Show the help menu")
    async def help_command(ctx):
        view = HelpView(bot)
        page = view.pages[0]
        embed = discord.Embed(title=page["title"], description=page["description"], color=discord.Color.blue())
        for field in page["fields"]:
            embed.add_field(name=field["name"], value=field["value"], inline=False)
        await ctx.respond(embed=embed, view=view)