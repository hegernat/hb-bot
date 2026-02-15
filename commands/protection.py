import discord
from game.utils import fmt
from db.queries import get_player, create_player
from db.db import get_db
from game.locations import get_location_index

BASE_COST = 15_000
MAX_TIER = 3

def next_cost(tier: int, player) -> int:
    location_index = get_location_index(player["location"])
    prestige_level = player["prestige_level"] or 0

    tier_multiplier = 1 + (0.30 * tier)
    location_multiplier = 1 + (0.50 * location_index)
    prestige_multiplier = 1 + (0.05 * prestige_level)

    return int(
        BASE_COST *
        tier_multiplier *
        location_multiplier *
        prestige_multiplier
    )
    
def register(bot):

    async def kind_autocomplete(ctx: discord.AutocompleteContext):
        return ["mold", "raid"]

    @bot.slash_command(
        name="protection",
        description="Buy protection from mold & raids"
    )
    async def protection(
        ctx: discord.ApplicationContext,
        kind: discord.Option(str, autocomplete=kind_autocomplete)
    ):
        user_id = ctx.author.id
        kind = kind.lower()

        if kind not in ["mold", "raid"]:
            await ctx.respond("Choose mold or raid.", ephemeral=True)
            return

        player = get_player(user_id)
        if not player:
            create_player(user_id)
            player = get_player(user_id)

        db = get_db()

        if kind == "mold":
            tier = player["mold_protection"] or 0
            field = "mold_protection"
        else:
            tier = player["raid_protection"] or 0
            field = "raid_protection"

        if tier >= MAX_TIER:
            await ctx.respond(
                f"{ctx.author.mention}\n"
                f"{kind.capitalize()} protection is already max tier ({MAX_TIER}).",
                ephemeral=True
            )
            return

        cost = next_cost(tier, player)

        if player["cash"] < cost:
            await ctx.respond(
                f"{ctx.author.mention}\n"
                f"Current tier: {tier}\n"
                f"Next upgrade cost: €{fmt(cost)}\n"
                f"You do not have enough cash.",
                ephemeral=True
            )
            return

        # Deduct cash and increase tier
        db.execute(
            f"""
            UPDATE players
            SET {field} = {field} + 1,
                cash = cash - ?
            WHERE user_id = ?
            """,
            (cost, user_id)
        )
        db.commit()

        new_tier = tier + 1

        await ctx.respond(
            f"{ctx.author.mention}\n"
            f"{kind.capitalize()} protection upgraded.\n"
            f"New tier: {new_tier}\n"
            f"Cost: €{fmt(cost)}"
        )