import discord
from game.utils import fmt, to_roman
from db.queries import (
    get_player,
    create_player,
    update_player_resources,
    delete_batch,
)
from game.locations import LOCATIONS, get_location_index
from db.db import get_db


PRESTIGE_BASE_XP = 1_000_000


def prestige_required_xp(level: int) -> int:
    return int(PRESTIGE_BASE_XP * (1 + 0.05 * level))


def register(bot, GUILD_ID):

    @bot.slash_command(
        name="prestige",
        description="Reset progress and gain permanent bonuses"
    )
    async def prestige(ctx: discord.ApplicationContext):
        user_id = ctx.author.id

        player = get_player(user_id)
        if not player:
            create_player(user_id)
            player = get_player(user_id)

        current_index = get_location_index(player["location"])
        last_index = len(LOCATIONS) - 1

        if current_index < last_index:
            await ctx.respond(
                "You must reach the final location to prestige.",
                ephemeral=True
            )
            return

        current_prestige = player["prestige_level"]
        required_xp = prestige_required_xp(current_prestige)

        if player["current_xp"] < required_xp:
            missing = required_xp - player["current_xp"]

            await ctx.respond(
                f"Prestige requires **{fmt(required_xp)} XP**.\n"
                f"You are missing **{fmt(missing)} XP**.",
                ephemeral=True
            )
            return

        new_prestige = current_prestige + 1

        db = get_db()
        db.execute(
            """
            UPDATE players
            SET current_xp = 0,
                sugar = 0,
                yeast = 0,
                moonshine = 0,
                cash = 500,
                location = ?,
                prestige_level = ?,
                mold_protection = 0,
                raid_protection = 0
            WHERE user_id = ?
            """,
            ("Shed", new_prestige, user_id)
        )
        
        db.commit()

        delete_batch(user_id)

        bonus_pct = player["prestige_level"] * 5

        await ctx.respond(
            f"{ctx.author.mention}\n"
            f"**Prestige complete.**\n\n"
            f"Prestige Level: {to_roman(new_prestige)}\n"
            f"Brewing Speed Bonus: +{bonus_pct}%\n"
            f"XP Requirement Scaling: +5% per prestige level\n\n"
            f"Progress reset to Shed.\n"
            f"Starting cash: €500"
)
