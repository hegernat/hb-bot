import random
import discord
from game.utils import fmt
from game.utils import format_time
from game.utils import is_prestige_eligible
from game.brewing import resolve_batch_if_needed
from db.queries import (
    get_player,
    create_player,
    update_player_resources,
    add_xp,
    set_prestige_notified,
)

def register(bot, GUILD_ID):

    @bot.slash_command(
        name="sell",
        description="Sell your liquour"
    )
    async def sell(
        ctx: discord.ApplicationContext,
        amount: str,
    ):
        user_id = ctx.author.id

        # -----------------------------------------------------
        # Resolve finished brew first
        # -----------------------------------------------------
        result = resolve_batch_if_needed(user_id)
        if result:
            if result["type"] == "complete":
                await ctx.channel.send(
                    f"{ctx.author.mention} Your batch of "
                    f"**{result['liters']} liters** has finished brewing."
                )
            elif result["type"] == "mold":
                await ctx.channel.send(
                    f"{ctx.author.mention} Your batch was **ruined by mold**.\n"
                    f"You salvaged **{result['refund_sugar']} sugar** "
                    f"and **{result['refund_yeast']} yeast**."
                )

        # -----------------------------------------------------
        # Get player
        # -----------------------------------------------------
        player = get_player(user_id)
        if not player:
            create_player(user_id)
            player = get_player(user_id)

        stored = player["moonshine"]
        amount = amount.lower().strip()

        if stored <= 0:
            await ctx.respond(
                "You have no moonshine to sell.",
                ephemeral=True
            )
            return

        # -----------------------------------------------------
        # Resolve amount
        # -----------------------------------------------------
        if amount == "all":
            qty = stored
        elif amount == "half":
            qty = stored // 2
        else:
            if not amount.isdigit():
                await ctx.respond(
                    "Amount must be a number, `all`, or `half`.",
                    ephemeral=True
                )
                return
            qty = int(amount)

        if qty <= 0:
            await ctx.respond(
                "You can't sell zero or negative amounts.",
                ephemeral=True
            )
            return

        if qty > stored:
            await ctx.respond(
                f"You only have **{stored} liters** available.",
                ephemeral=True
            )
            return

        # -----------------------------------------------------
        # Pricing
        # -----------------------------------------------------
        price_per_liter = random.randint(10, 12)

        prestige = player["prestige_level"] or 0
        sale_multiplier = 1 + (0.05 * prestige)

        gross_revenue = int(qty * price_per_liter * sale_multiplier)
        xp_gained = qty * 10

        # -----------------------------------------------------
        # RAID LOGIC
        # -----------------------------------------------------
        prestige = player["prestige_level"]

        base_risk = min(prestige, 5)
        extra_risk = qty // 5000
        raid_risk_percent = min(base_risk + extra_risk, 10)

        raid_tier = player["raid_protection"] or 0
        raid_risk_percent *= (1 - raid_tier * 0.25)
        raid_risk_percent = int(raid_risk_percent)

        raid_triggered = random.randint(1, 100) <= raid_risk_percent

        final_revenue = gross_revenue
        raid_loss_percent = 0

        if raid_triggered and raid_risk_percent > 0:
            raid_loss_percent = random.randint(50, 80)
            loss_amount = (gross_revenue * raid_loss_percent) // 100
            final_revenue = gross_revenue - loss_amount

        # -----------------------------------------------------
        # APPLY SALE
        # -----------------------------------------------------
        update_player_resources(
            user_id,
            moonshine_delta=-qty,
            cash_delta=final_revenue,
        )

        add_xp(user_id, xp_gained)

        # -----------------------------------------------------
        # MAIN RESPONSE (must be first respond)
        # -----------------------------------------------------
        if raid_triggered and raid_risk_percent > 0:
            await ctx.respond(
                f"**POLICE RAID!**\n\n"
                f"{ctx.author.mention} Authorities intercepted your sale.\n\n"
                f"Sold: {fmt(qty)} liters\n"
                f"Cash received: €{fmt(final_revenue)} (of €{fmt(gross_revenue)})\n"
                f"XP gained: {fmt(xp_gained)}"

            )
        else:
            await ctx.respond(
                f"{ctx.author.mention}\nSold {fmt(qty)} liters "
                f"for €{fmt(gross_revenue)} (€{fmt(price_per_liter)}/L)\n"
                f"XP gained: {fmt(xp_gained)}"
            )

        # -----------------------------------------------------
        # PRESTIGE CHECK (followup only)
        # -----------------------------------------------------
        player = get_player(user_id)

        if is_prestige_eligible(player) and not player["prestige_notified"]:
            await ctx.followup.send(
                f"{ctx.author.mention}\nYou are eligible for "
                f"**PRESTIGE**! Use `/prestige` to advance."
            )
            set_prestige_notified(user_id)