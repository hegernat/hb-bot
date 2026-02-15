import discord
import time
import random

from db.queries import (
    get_player,
    create_player,
    update_player_resources,
    get_active_batch,
    create_batch,
)

from game.brewing import resolve_batch_if_needed
from game.locations import LOCATIONS, get_location_index
from game.utils import fmt, format_time

# Brewing ratios
RATIO_SUGAR = 5
RATIO_YEAST = 1
BASE_MOLD_RISK = 0.15


def register(bot):

    @bot.slash_command(
        name="brew",
        description="Start brewing liquor"
    )
    async def brew(
        ctx: discord.ApplicationContext,
        amount: discord.Option(
            str,
            "Amount in liters or 'all'",
            required=False
        ) = None,
    ):

        user_id = ctx.author.id
        now = int(time.time())

        # --- load player ---
        player = get_player(user_id)
        if not player:
            create_player(user_id)
            player = get_player(user_id)

        # resolve finished batch first
        result = resolve_batch_if_needed(user_id)
        if result:
            if result["type"] == "complete":
                gained = result["liters"]
                overflow = result.get("overflow", 0)

                message = (
                    f"{ctx.author.mention}\n"
                    f"Brew completed.\n"
                    f"Liquor gained: {fmt(gained)} liters"
                )

                if overflow > 0:
                    message += f"\nLost due to full storage: {fmt(overflow)}L"

                await ctx.respond(message)
                return

            elif result["type"] == "mold":
                await ctx.respond(
                    f"{ctx.author.mention}\nBrew failed due to mold."
                )
                return

        player = get_player(user_id)

        # --- check active batch ---
        batch = get_active_batch(user_id)
        if batch:
            remaining = max(0, batch["end_time"] - now)
            await ctx.respond(
                f"{ctx.author.mention}\nYou're already brewing.\n"
                f"Batch completes in **{format_time(remaining)}**."
            )
            return

        # --- storage info ---
        current_moonshine = player["moonshine"] or 0
        location_index = get_location_index(player["location"])
        max_storage = LOCATIONS[location_index]["max_storage"]

        if current_moonshine >= max_storage:
            await ctx.respond(
                f"{ctx.author.mention}\nStorage is full.",
                ephemeral=True
            )
            return

        remaining_capacity = max_storage - current_moonshine

        # --- ingredient limits ---
        max_by_sugar = player["sugar"] // RATIO_SUGAR
        max_by_yeast = player["yeast"] // RATIO_YEAST
        max_batches = min(max_by_sugar, max_by_yeast)

        if max_batches <= 0:
            await ctx.respond(
                "Not enough ingredients to brew.",
                ephemeral=True
            )
            return

        max_liters_by_ingredients = max_batches * RATIO_SUGAR

        # --------------------------------------------------
        # DETERMINE LITERS TO BREW
        # --------------------------------------------------

        if amount is None:
            # default = brew max possible without overflow
            target_liters = min(
                remaining_capacity,
                max_liters_by_ingredients
            )

        else:
            amount = amount.lower().strip()

            if amount == "all":
                target_liters = min(
                    remaining_capacity,
                    max_liters_by_ingredients
                )
            else:
                # support 5k
                if amount.endswith("k"):
                    try:
                        target_liters = int(amount[:-1]) * 1000
                    except ValueError:
                        await ctx.respond(
                            "Invalid amount format.",
                            ephemeral=True
                        )
                        return
                else:
                    try:
                        target_liters = int(amount)
                    except ValueError:
                        await ctx.respond(
                            "Invalid amount.",
                            ephemeral=True
                        )
                        return

                if target_liters <= 0:
                    await ctx.respond(
                        "Amount must be positive.",
                        ephemeral=True
                    )
                    return

                # cap by storage & ingredients
                target_liters = min(
                    target_liters,
                    remaining_capacity,
                    max_liters_by_ingredients
                )

        if target_liters <= 0:
            await ctx.respond(
                "Nothing to brew.",
                ephemeral=True
            )
            return

        # convert liters → batches
        batches = target_liters // RATIO_SUGAR
        liters = batches * RATIO_SUGAR

        if liters <= 0:
            await ctx.respond(
                "Not enough ingredients for that amount.",
                ephemeral=True
            )
            return

        sugar_used = batches * RATIO_SUGAR
        yeast_used = batches * RATIO_YEAST

        # --- prestige speed bonus ---
        prestige_level = player["prestige_level"] or 0
        speed_multiplier = 1 - (0.05 * prestige_level)
        duration = round(liters * speed_multiplier)

        # --- mold risk ---
        mold_tier = player["mold_protection"] or 0
        effective_risk = BASE_MOLD_RISK * (1 - mold_tier * 0.25)
        effective_risk = max(0, effective_risk)

        will_fail = random.random() < effective_risk
        fail_time = None

        start_ts = now
        end_ts = now + duration

        if will_fail and duration > 1:
            fail_time = random.randint(start_ts + 1, end_ts - 1)

        # --- consume ingredients ---
        update_player_resources(
            user_id,
            sugar_delta=-sugar_used,
            yeast_delta=-yeast_used,
        )

        # --- create batch ---
        create_batch(
            user_id=user_id,
            liters=liters,
            start_time=start_ts,
            end_time=end_ts,
            will_fail=will_fail,
            fail_time=fail_time,
            channel_id=ctx.channel.id
        )

        await ctx.respond(
            f"{ctx.author.mention}\n"
            f"Started brewing {fmt(liters)} liters\n"
            f"Time remaining: {format_time(duration)}"
        )