import discord
from game.utils import fmt
from game.utils import format_time
from db.queries import (
    get_player,
    create_player,
    update_player_resources,
)
from game.locations import LOCATIONS, get_location_index

PRICES = {
    "sugar": 1,
    "yeast": 2,
}


def register(bot):

    @bot.slash_command(
        name="buy",
        description="Buy ingredients for brewing"
    )
    async def buy(
        ctx: discord.ApplicationContext,
        resource: discord.Option(
            str,
            choices=["sugar", "yeast"],
            description="What to buy"
        ),
        amount: str,
    ):
        resource = resource.lower().strip()
        amount = amount.lower().strip()

        user_id = ctx.author.id
        player = get_player(user_id)

        if not player:
            create_player(user_id)
            player = get_player(user_id)

        loc_index = get_location_index(player["location"])
        location = LOCATIONS[loc_index]
        price = PRICES[resource]

        # --- storage limits ---
        max_storage = location[f"max_{resource}"]
        current_amount = player[resource]
        free_space = max_storage - current_amount

        if free_space <= 0:
            await ctx.respond(
                f"Your {resource} storage is full.",
                ephemeral=True
            )
            return

        cash = player["cash"]

        # --- resolve amount ---
        if amount == "all":
            qty = cash // price
        elif amount == "half":
            qty = (cash // price) // 2
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
                "You can't buy zero or negative amounts.",
                ephemeral=True
            )
            return

        # --- enforce storage limit ---
        qty = min(qty, free_space)

        cost = qty * price

        if cost > cash:
            await ctx.respond(
                f"{ctx.author.mention} Not enough cash.\nYou need €{cost}, you have €{cash}.",
                ephemeral=True
            )
            return

        update_player_resources(
            user_id,
            cash_delta=-cost,
            sugar_delta=qty if resource == "sugar" else 0,
            yeast_delta=qty if resource == "yeast" else 0,
        )

        await ctx.respond(
            f"{ctx.author.mention}\n"
            f"Purchased {fmt(qty)} {resource} for €{fmt(cost)}.\n"
            f"Storage: {fmt(current_amount + qty)}/{fmt(max_storage)}\n"
        )