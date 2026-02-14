import time
import random
import discord
from game.utils import fmt
from game.utils import format_time
from game.brewing import resolve_batch_if_needed
from game.locations import LOCATIONS, get_location_index

from db.queries import (
    get_player,
    create_player,
    update_player_resources,
    get_active_batch,
    create_batch,
)

RATIO_SUGAR = 5
RATIO_YEAST = 1

BASE_MOLD_RISK = 0.03  # 3 % baseline

def register(bot, GUILD_ID):

    @bot.slash_command(
        name="brew",
        description="Start brewing liqour"
    )
    async def brew(ctx: discord.ApplicationContext):


        user_id = ctx.author.id
        now = int(time.time())

        # --- load player ---
        player = get_player(user_id)
        if not player:
            create_player(user_id)
            player = get_player(user_id)

        result = resolve_batch_if_needed(user_id)
        batch = get_active_batch(user_id)

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
                    f"{ctx.author.mention}\n"
                    f"Brew failed due to mold."
                )
                return

        # reload player after resolve
        player = get_player(user_id)
        current_moonshine = player["moonshine"] or 0
        location_index = get_location_index(player["location"])
        location = LOCATIONS[location_index]
        max_storage = location["max_storage"]

        # --- check existing batch ---
        batch = get_active_batch(user_id)
        if batch:
            remaining = max(0, batch["end_time"] - now)
            time_str = format_time(remaining)

            await ctx.respond(
                f"{ctx.author.mention}\nYou're already brewing.\n"
                f"Batch completes in **{time_str}**."
            )
            return

        if current_moonshine >= max_storage:
            await ctx.respond(
                f"{ctx.author.mention}\n"
                f"Your storage is full.\n"
                f"Liquor: {current_moonshine}/{max_storage}\n"
                f"Sell or upgrade location before brewing again.",
                ephemeral=True
            )
            return


        # --- calculate max possible batch ---
        max_by_sugar = player["sugar"] // RATIO_SUGAR
        max_by_yeast = player["yeast"] // RATIO_YEAST

        max_batches = min(max_by_sugar, max_by_yeast)

        if max_batches <= 0:
            await ctx.respond(
                "You don't have enough ingredients to brew.",
                ephemeral=True
            )
            return
            
        liters = max_batches * RATIO_SUGAR   # 1 unit = 5 liters    

        # --- prestige speed bonus ---
        prestige_level = player["prestige_level"] or 0
        speed_multiplier = 1 - (0.05 * prestige_level)

        duration = round(liters * speed_multiplier)

        # --- block brew if batch would overflow storage ---
        current_moonshine = player["moonshine"] or 0
        location_index = get_location_index(player["location"])
        location = LOCATIONS[location_index]
        max_storage = location["max_storage"]

        if current_moonshine + liters > max_storage:
            space_left = max_storage - current_moonshine

            await ctx.respond(
                f"{ctx.author.mention}\n"
                f"Not enough storage space.\n"
                f"Storage: {fmt(current_moonshine)}/{fmt(max_storage)}L\n"
                f"Free space: {fmt(space_left)}L\n"
                f"Batch size: {fmt(liters)}L\n"
                f"Sell moonshine or upgrade location.",
                ephemeral=True
            )
            return


        # säkerställ att vi inte går under 50% hastighet
        sugar_used = max_batches * RATIO_SUGAR
        yeast_used = max_batches * RATIO_YEAST

        # --- mold risk calculation ---
        mold_tier = player["mold_protection"] or 0

        # each tier reduces risk by 25%
        effective_risk = BASE_MOLD_RISK * (1 - mold_tier * 0.25)

        # clamp safety
        if effective_risk < 0:
            effective_risk = 0

        will_fail = random.random() < effective_risk
        fail_time = None

        start_ts = now
        end_ts = now + duration

        if will_fail and duration > 1:
            fail_time = random.randint(start_ts + 1, end_ts - 1)

        current_moonshine = player["moonshine"] or 0
        location_index = get_location_index(player["location"])
        location = LOCATIONS[location_index]
        max_storage = location["max_storage"]
        
        # --- consume ingredients ONLY NOW ---
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

        time_str = format_time(duration)

        await ctx.respond(
            f"{ctx.author.mention}\n"
            f"Started brewing {fmt(liters)} liters\n"
            f"Time remaining: {time_str}"
        )