import discord
from discord.ext import commands
from ui_components import TruthDareView

special_role_ids = [1108963523964448848, 1259144610366619740]  # Replace with actual role IDs
special_channel_ids = [1109009867240382526]  # Replace with actual channel IDs

def setup_commands(bot, question_manager, db_manager):
    @bot.slash_command(name="truth", description="Get a truth question")
    async def truth(ctx):
        await handle_command(ctx, 'truth', question_manager, db_manager)

    @bot.slash_command(name="dare", description="Get a dare question")
    async def dare(ctx):
        await handle_command(ctx, 'dare', question_manager, db_manager)

    @bot.slash_command(name="random", description="Get a random truth or dare question")
    async def random_question(ctx):
        await handle_command(ctx, 'random', question_manager, db_manager)

    @bot.slash_command(name="set_rating", description="Set your preferred maximum rating")
    async def set_rating(ctx, rating: int):
        if rating < 1 or rating > 18:
            await ctx.respond("Rating must be between 1 and 18.", ephemeral=True)
            return

        db_manager.set_user_rating(ctx.author.id, rating)
        await ctx.respond(f"Your maximum rating has been set to {rating}.", ephemeral=True)

    @bot.slash_command(name="view_rating", description="View your or another user's maximum rating")
    async def view_rating(ctx, user: discord.Member = None):
        target_user = user or ctx.author
        rating = db_manager.get_user_rating(target_user.id)

        if rating is None:
            response = f"{target_user.display_name} hasn't set a maximum rating yet. The default rating of 13 will be used."
        else:
            response = f"{target_user.display_name}'s maximum rating is set to {rating}."

        await ctx.respond(response, ephemeral=True)

async def handle_command(ctx, command_type, question_manager, db_manager):
    max_rating = db_manager.get_user_rating(ctx.author.id) or 13  # Default to 13 if not set

    if max_rating > 18 and not (
        any(role.id in special_role_ids for role in ctx.author.roles) and
        ctx.channel.id in special_channel_ids
    ):
        await ctx.respond("You don't have permission to access 18+ questions in this channel.", ephemeral=True)
        return

    if command_type == 'random':
        question = question_manager.get_random_question(max_rating)
        question_type = 'TRUTH' if question in question_manager.truths else 'DARE'
    else:
        question = question_manager.get_question(command_type, max_rating)
        question_type = command_type.upper()

    embed = discord.Embed(title=question['question'], color=discord.Color.blue())
    embed.set_footer(text=f"TYPE: {question_type} | RATING: {question['maxrating']} | ID: {question['ID']}")
    embed.set_author(name=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

    view = TruthDareView(question_manager, db_manager, ctx.author)
    await ctx.respond(embed=embed, view=view)