import discord
from game.utils import fmt
from game.utils import format_time
from db.queries import get_player, create_player, update_player_resources
from game.locations import LOCATIONS, get_location_index
from game.brewing import resolve_batch_if_needed

def register(bot, GUILD_ID):

    @bot.slash_command(
        guild_ids=[GUILD_ID],
        name="upgrade",
        description="Upgrade your location"
    )
    async def upgrade(ctx: discord.ApplicationContext):
        user_id = ctx.author.id

        # Resolve finished brew first
        result = resolve_batch_if_needed(user_id)

        player = get_player(user_id)
        if not player:
            create_player(user_id)
            player = get_player(user_id)

        current_index = get_location_index(player["location"])

        # Already maxed
        if current_index >= len(LOCATIONS) - 1:
            await ctx.respond(
                "You already own the best location available.",
                ephemeral=True
            )
            return

        current_loc = LOCATIONS[current_index]
        next_loc = LOCATIONS[current_index + 1]

        if next_loc["upgrade_xp"] is None or next_loc["upgrade_cost"] is None:
            await ctx.respond(
                "You are upgrading to the final location.",
                ephemeral=True
            )
            xp_required = 0
            cash_required = 0
        else:
            xp_required = next_loc["upgrade_xp"]
            cash_required = next_loc["upgrade_cost"]

        # --- Requirements ---

        xp_required = next_loc["upgrade_xp"]
        cash_required = next_loc["upgrade_cost"]

        current_xp = player["current_xp"] or 0
        missing_xp = max(0, xp_required - current_xp)
        missing_cash = max(0, cash_required - player["cash"])

        if missing_xp > 0 or missing_cash > 0:
            msg = "Upgrade requirements not met:\n"
            if missing_xp > 0:
                msg += f"- Missing XP: {fmt(missing_xp)}\n"
            if missing_cash > 0:
                msg += f"- Missing cash: €{fmt(missing_cash)}\n"

            await ctx.respond(msg, ephemeral=True)
            return

        # --- Apply upgrade ---
        update_player_resources(
            user_id,
            cash_delta=-cash_required
        )

        # Update location directly
        from db.db import get_db
        db = get_db()
        db.execute(
            "UPDATE players SET location = ? WHERE user_id = ?",
            (next_loc["name"], user_id)
        )
        db.commit()

        # Starter cash for new location
        update_player_resources(
            user_id,
            cash_delta=200
        )

        await ctx.respond(
            f"<@{user_id}> \nLocation upgraded!\n"
            f"{current_loc['name']} → **{next_loc['name']}**\n\n"
        )
        await ctx.respond("Upgrade works")