import discord
from game.utils import fmt
from game.utils import to_roman
from commands.prestige import prestige_required_xp

from db.queries import (
    get_player,
    create_player,
    get_global_rank,
)

def register(bot):

    @bot.slash_command(
        name="profile",
        description="View user profiles"
    )
    async def profile(ctx, user: discord.Member = None):

        target = user or ctx.author
        player = get_player(target.id)

        if not player:
            await ctx.respond("Player not found.", ephemeral=True)
            return

        rank = get_global_rank(target.id)

        embed = discord.Embed(
            title=f"{target.name} — Profile",
            color=discord.Color.dark_gray()
        )

        embed.add_field(
            name="Rank",
            value=f"#{rank}" if rank else "N/A",
            inline=True
        )

        embed.add_field(
            name="Prestige",
            value=to_roman(player["prestige_level"]),
            inline=True
        )

        embed.add_field(
            name="XP",
            value=(
                f"Current: {fmt(player['current_xp'])}\n"
                f"Total: {fmt(player['total_xp'])}"
            ),
            inline=False
        )

        embed.add_field(
            name="Location",
            value=player["location"],
            inline=False
        )

        await ctx.respond(embed=embed)