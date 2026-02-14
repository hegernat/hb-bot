import time
import discord
from game.utils import fmt
from game.utils import format_time
from game.utils import to_roman
from db.queries import get_player, create_player, get_active_batch
from game.brewing import resolve_batch_if_needed
from game.locations import LOCATIONS, get_location_index

def register(bot, GUILD_ID):

    @bot.slash_command(
        name="inventory",
        description="View your inventory"
    )
    async def inventory(ctx: discord.ApplicationContext):
        user_id = ctx.author.id

        # resolve finished brew first (and send notification if needed)
        result = resolve_batch_if_needed(user_id)

        if result and result["type"] == "complete":
            await ctx.channel.send(
                f"<@{user_id}>\nFinished brewing {fmt(result['liters'])} liters."
            )

        elif result and result["type"] == "mold":
            await ctx.channel.send(
                f"<@{user_id}>\nYour batch was **ruined by mold**.\n"
                f"You salvaged {fmt(result['refund_sugar'])} sugar "
                f"and **{fmt(result['refund_yeast'])} yeast."
            )


        player = get_player(user_id)
        if not player:
            create_player(user_id)
            player = get_player(user_id)

        loc_index = get_location_index(player["location"])
        location = LOCATIONS[loc_index]

        embed = discord.Embed(
            title="HB — Inventory",
            color=discord.Color.dark_gold()
        )

        embed.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.display_avatar.url
        )

        # --- Location & Cash ---
        embed.add_field(
            name="Location",
            value=location["name"],
            inline=True
        )
        embed.add_field(
            name="Cash",
            value=f"€{fmt(player['cash'])}",
            inline=True
        )

        # --- Ingredients ---
        embed.add_field(
            name="Ingredients",
            value=(
                f"Sugar: {fmt(player['sugar'])} / {fmt(location['max_sugar'])}\n"
                f"Yeast: {fmt(player['yeast'])} / {fmt(location['max_yeast'])}"
            ),
            inline=False
        )

        # --- Moonshine ---
        embed.add_field(
            name="Liquor",
            value=f"{fmt(player['moonshine'])} / {fmt(location['max_storage'])}",
            inline=False
        )

        mold_tier = player["mold_protection"] or 0
        raid_tier = player["raid_protection"] or 0

        embed.add_field(
            name="Protection",
            value=(
                f"Mold: Tier {mold_tier}\n"
                f"Raid: Tier {raid_tier}"
            ),
            inline=False
        )

        # --- Brewing status (only if active) ---
        batch = get_active_batch(user_id)
        if batch:
            now = int(time.time())
            remaining = max(0, batch["end_time"] - now)
            time_str = format_time(remaining)

            embed.add_field(
                name="Brewing",
                value=f"In progress ({time_str} remaining)",
                inline=False
            )


        # --- Progress ---
        embed.add_field(
            name="Progress",
            value=(
                f"Current XP: {fmt(player['current_xp'])}\n"
                f"Total XP: {fmt(player['total_xp'])}\n"
                f"Prestige: {to_roman(player['prestige_level'])}"
            ),
            inline=False
        )

        await ctx.respond(embed=embed)