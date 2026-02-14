import discord
from game.utils import fmt
from game.utils import format_time
from db.queries import get_top_players
from game.utils import to_roman

def register(bot, GUILD_ID):

    @bot.slash_command(
        name="leaderboard",
        description="View global leaderboard"
    )
    async def leaderboard(ctx: discord.ApplicationContext):
        rows = get_top_players(10)

        if not rows:
            await ctx.respond("No players on the leaderboard yet.")
            return

        embed = discord.Embed(
            title="Global Leaderboard",
            color=discord.Color.dark_gray()
        )

        rank_lines = []
        name_lines = []
        prestige_lines = []
        xp_lines = []

        rank = 1
        for row in rows:
            user_id = row["user_id"]
            total_xp = row["total_xp"]
            prestige = row["prestige_level"]

            try:
                user = await bot.fetch_user(user_id)
                name = user.name
            except:
                name = f"User {user_id}"

            rank_lines.append(str(rank))
            name_lines.append(name)
            prestige_lines.append(to_roman(prestige))
            xp_lines.append(fmt(total_xp))

            rank += 1

        embed.add_field(
            name="#",
            value="\n".join(rank_lines),
            inline=True
        )
        embed.add_field(
            name="User",
            value="\n".join(name_lines),
            inline=True
        )
        embed.add_field(
            name="Total XP",
            value="\n".join(xp_lines),
            inline=True
        )

        await ctx.respond(embed=embed)
