import discord
from discord.ext import commands

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="set_rating", description="Set your preferred question rating")
    async def set_rating(self, ctx, rating: int):
        if rating < 0 or rating > 18:
            await ctx.respond("Rating must be between 0 and 18.", ephemeral=True)
            return

        truth_dare_cog = self.bot.get_cog("TruthDare")
        if truth_dare_cog:
            truth_dare_cog.user_ratings[ctx.author.id] = rating
            await ctx.respond(f"Your rating has been set to {rating}.", ephemeral=True)
        else:
            await ctx.respond("Unable to set rating. Please try again later.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Settings(bot))