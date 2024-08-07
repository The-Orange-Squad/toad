import discord
from discord.ext import commands
from ui_components import TruthDareView

special_role_ids = [123456789, 987654321]  # Replace with actual role IDs
special_channel_ids = [111222333, 444555666]  # Replace with actual channel IDs

user_ratings = {}

def setup_commands(bot, question_manager):
    @bot.slash_command(name="truth", description="Get a truth question")
    async def truth(ctx):
        await handle_command(ctx, 'truth', question_manager)

    @bot.slash_command(name="dare", description="Get a dare question")
    async def dare(ctx):
        await handle_command(ctx, 'dare', question_manager)

    @bot.slash_command(name="random", description="Get a random truth or dare question")
    async def random_question(ctx):
        await handle_command(ctx, 'random', question_manager)

    @bot.slash_command(name="set_rating", description="Set your preferred maximum rating")
    async def set_rating(ctx, rating: int):
        if rating < 1 or rating > 18:
            await ctx.respond("Rating must be between 1 and 18.", ephemeral=True)
            return

        user_ratings[ctx.author.id] = rating
        await ctx.respond(f"Your maximum rating has been set to {rating}.", ephemeral=True)

async def handle_command(ctx, command_type, question_manager):
    max_rating = user_ratings.get(ctx.author.id, 13)  # Default to 13 if not set

    if max_rating > 18 and not (
        any(role.id in special_role_ids for role in ctx.author.roles) and
        ctx.channel.id in special_channel_ids
    ):
        await ctx.respond("You don't have permission to access 18+ questions in this channel.", ephemeral=True)
        return

    view = TruthDareView(question_manager, max_rating)
    embed = discord.Embed(title="Truth or Dare?", description="Choose your fate!", color=discord.Color.blue())
    await ctx.respond(embed=embed, view=view)