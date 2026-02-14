import discord
from game.utils import fmt
from db.queries import get_player, create_player, update_player_resources

SUGAR_PRICE = 1
YEAST_PRICE = 2

def register(bot, GUILD_ID):

    # -------------------------
    # AUTOCOMPLETE
    # -------------------------
    async def resource_autocomplete(ctx: discord.AutocompleteContext):
        return ["sugar", "yeast"]

    @bot.slash_command(
        name="resell",
        description="Resell youre ingredients"
    )
    async def resell(
        ctx: discord.ApplicationContext,
        resource: discord.Option(str, autocomplete=resource_autocomplete),
        amount: str
    ):
        user_id = ctx.author.id
        resource = resource.lower().strip()

        if resource not in ["sugar", "yeast"]:
            await ctx.respond(
                "Resource must be sugar or yeast.",
                ephemeral=True
            )
            return

        player = get_player(user_id)
        if not player:
            create_player(user_id)
            player = get_player(user_id)

        owned = player[resource]

        if owned <= 0:
            await ctx.respond(
                f"You have no {resource} to resell.",
                ephemeral=True
            )
            return

        amount_input = amount.lower().strip()

        # -------------------------
        # ALL
        # -------------------------
        if amount_input == "all":
            sell_amount = owned

        # -------------------------
        # HALF
        # -------------------------
        elif amount_input == "half":
            sell_amount = owned // 2
            if sell_amount <= 0:
                await ctx.respond(
                    f"You do not have enough {resource} to resell half.",
                    ephemeral=True
                )
                return

        # -------------------------
        # NUMERIC
        # -------------------------
        else:
            if not amount_input.isdigit():
                await ctx.respond(
                    "Amount must be a positive number, 'all', or 'half'.",
                    ephemeral=True
                )
                return

            sell_amount = int(amount_input)

            if sell_amount <= 0:
                await ctx.respond(
                    "Amount must be greater than zero.",
                    ephemeral=True
                )
                return

            if sell_amount > owned:
                await ctx.respond(
                    f"You only have {fmt(owned)} {resource}.",
                    ephemeral=True
                )
                return

        # -------------------------
        # REFUND CALC
        # -------------------------
        base_price = SUGAR_PRICE if resource == "sugar" else YEAST_PRICE
        refund = sell_amount * base_price

        if resource == "sugar":
            update_player_resources(
                user_id,
                sugar_delta=-sell_amount,
                cash_delta=refund
            )
        else:
            update_player_resources(
                user_id,
                yeast_delta=-sell_amount,
                cash_delta=refund
            )

        await ctx.respond(
            f"{ctx.author.mention}\n"
            f"Resold **{fmt(sell_amount)} {resource}**\n"
            f"Refund received: **€{fmt(refund)}**"
        )
