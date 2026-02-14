import random
import discord
import time

from game.locations import get_location_index, LOCATIONS
from game.market import generate_market
from game.utils import fmt, is_prestige_eligible
from game.brewing import resolve_batch_if_needed

from db.queries import (
    get_exposure,
    set_exposure,
    get_player,
    create_player,
    update_player_resources,
    add_xp,
    set_prestige_notified,
)


def register(bot, GUILD_ID):

    # -------------------------------------------------
    # AUTOCOMPLETE FUNCTION
    # -------------------------------------------------
    async def buyer_autocomplete(ctx: discord.AutocompleteContext):
        user_id = ctx.interaction.user.id
        player = get_player(user_id)
        if not player:
            return []

        location_index = get_location_index(player["location"])
        offers = generate_market(location_index)

        return [
            discord.OptionChoice(
                name=f"#{o['slot']} — {o['name']}",
                value=o["slot"]
            )
            for o in offers
        ]

    # -------------------------------------------------
    # SELL COMMAND
    # -------------------------------------------------
    @bot.slash_command(
        name="sell",
        description="Sell to a specific buyer"
    )
    async def sell(
        ctx: discord.ApplicationContext,
        buyer: discord.Option(
            int,
            "Select buyer",
            choices=[
                discord.OptionChoice("1 — HIV Rico", 1),
                discord.OptionChoice("2 — Drunk Daren", 2),
                discord.OptionChoice("3 — Syndicate Sam", 3),
            ],
        ),
    ):

        user_id = ctx.author.id

        result = resolve_batch_if_needed(user_id)
        if result:
            if result["type"] == "complete":
                await ctx.channel.send(
                    f"{ctx.author.mention}\nYour batch of "
                    f"**{result['liters']} liters** has finished brewing."
                )
            elif result["type"] == "mold":
                await ctx.channel.send(
                    f"{ctx.author.mention}\nYour batch was **ruined by mold**.\n"
                    f"You salvaged **{result['refund_sugar']} sugar** "
                    f"and **{result['refund_yeast']} yeast**."
                )

        player = get_player(user_id)
        if not player:
            create_player(user_id)
            player = get_player(user_id)

        stored = player["moonshine"]
        if stored <= 0:
            await ctx.respond("You have no moonshine to sell.", ephemeral=True)
            return

        location_index = get_location_index(player["location"])
        offers = generate_market(location_index)

        selected = next((o for o in offers if o["slot"] == buyer), None)
        if not selected:
            await ctx.respond("Invalid buyer slot. Use /market first.", ephemeral=True)
            return

        volume = random.randint(
            selected["volume_min"],
            selected["volume_max"]
        )
        volume = min(volume, stored)

        if volume <= 0:
            await ctx.respond("Not enough product for this deal.", ephemeral=True)
            return

        # Pricing
        xp_ratio = min(player["current_xp"] / 1_500_000, 1.0)
        price_multiplier = 1 + 0.06 * (xp_ratio ** 0.5)

        gross_revenue = int(volume * selected["price_per_liter"] * price_multiplier)
        xp_gained = volume * 10

        # Raid logic
        current_hour = int(time.time() // 3600)
        max_storage = LOCATIONS[location_index]["max_storage"]

        exposure = get_exposure(user_id, current_hour)

        exposure_ratio = (exposure + volume) / max_storage
        exposure_multiplier = 1 + (exposure_ratio ** 1.4) * 3

        xp_multiplier = 1 + (xp_ratio * 0.08)

        final_raid = selected["base_raid"] * exposure_multiplier * xp_multiplier
        final_raid = min(final_raid, 0.95)

        raid_triggered = random.random() < final_raid

        final_revenue = gross_revenue

        if raid_triggered:
            raid_loss_percent = random.randint(50, 80)

            protection_tier = player["raid_protection"] or 0
            protection_reduction = protection_tier * 0.15

            adjusted_loss_percent = raid_loss_percent * (1 - protection_reduction)
            loss_amount = int(gross_revenue * adjusted_loss_percent / 100)

            final_revenue = gross_revenue - loss_amount

        update_player_resources(
            user_id,
            moonshine_delta=-volume,
            cash_delta=final_revenue,
        )

        add_xp(user_id, xp_gained)

        exposure += volume
        set_exposure(user_id, current_hour, exposure)

        if raid_triggered:
            await ctx.respond(
                f"**POLICE RAID!**\n\n"
                f"Deal with **{selected['name']}** intercepted.\n\n"
                f"Sold: {fmt(volume)} L\n"
                f"Cash: €{fmt(final_revenue)} (of €{fmt(gross_revenue)})\n"
                f"XP gain: {fmt(xp_gained)}"
            )
        else:
            await ctx.respond(
                f"{ctx.author.mention}\nSold {fmt(volume)} liters to **{selected['name']}**\n"
                f"for €{fmt(gross_revenue)} "
                f"(€{selected['price_per_liter']}/L)\n"
                f"XP gain: {fmt(xp_gained)}"
            )

        player = get_player(user_id)

        if is_prestige_eligible(player) and not player["notified_prestige"]:
            await ctx.followup.send(
                "You are eligible for **PRESTIGE**! Use `/prestige`."
            )
            set_prestige_notified(user_id)