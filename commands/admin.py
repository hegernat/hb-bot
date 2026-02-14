import discord
from game.utils import fmt
from db.queries import (
    update_player_resources,
    add_xp,
    get_player,
    create_player,
)
from game.locations import LOCATIONS
from db.db import get_db


def is_owner(ctx):
    return ctx.author.id == ctx.guild.owner_id


def register(bot, GUILD_ID):

    # -------------------------
    # AUTOCOMPLETE FUNCTIONS
    # -------------------------

    async def add_remove_autocomplete(ctx: discord.AutocompleteContext):
        return ["cash", "xp", "sugar", "yeast"]

    async def set_autocomplete(ctx: discord.AutocompleteContext):
        return ["prestige", "location", "xp", "cash"]

    admin = bot.create_group(
        "admin",
        "Admin tools"
    )

    # =========================
    # ADD
    # =========================
    @admin.command(name="add")
    async def add(
        ctx: discord.ApplicationContext,
        field: discord.Option(str, autocomplete=add_remove_autocomplete),
        target: discord.User,
        amount: int
    ):
        if not is_owner(ctx):
            await ctx.respond("Nope.", ephemeral=True)
            return

        if amount <= 0:
            await ctx.respond("Amount must be positive.", ephemeral=True)
            return

        player = get_player(target.id)
        if not player:
            create_player(target.id)

        field = field.lower()

        if field == "cash":
            update_player_resources(target.id, cash_delta=amount)

        elif field == "xp":
            add_xp(target.id, amount)

        elif field == "sugar":
            update_player_resources(target.id, sugar_delta=amount)

        elif field == "yeast":
            update_player_resources(target.id, yeast_delta=amount)

        else:
            await ctx.respond("Invalid field.", ephemeral=True)
            return

        await ctx.respond(
            f"Added {fmt(amount)} {field} to {target.name}.",
            ephemeral=True
        )

    # =========================
    # REMOVE
    # =========================
    @admin.command(name="remove")
    async def remove(
        ctx: discord.ApplicationContext,
        field: discord.Option(str, autocomplete=add_remove_autocomplete),
        target: discord.User,
        amount: int
    ):
        if not is_owner(ctx):
            await ctx.respond("Nope.", ephemeral=True)
            return

        if amount <= 0:
            await ctx.respond("Amount must be positive.", ephemeral=True)
            return

        field = field.lower()

        if field == "cash":
            update_player_resources(target.id, cash_delta=-amount)

        elif field == "xp":
            add_xp(target.id, -amount)

        elif field == "sugar":
            update_player_resources(target.id, sugar_delta=-amount)

        elif field == "yeast":
            update_player_resources(target.id, yeast_delta=-amount)

        else:
            await ctx.respond("Invalid field.", ephemeral=True)
            return

        await ctx.respond(
            f"Removed {fmt(amount)} {field} from {target.name}.",
            ephemeral=True
        )

    # =========================
    # SET
    # =========================
    @admin.command(name="set")
    async def set_value(
        ctx: discord.ApplicationContext,
        field: discord.Option(str, autocomplete=set_autocomplete),
        target: discord.User,
        value: int
    ):
        if not is_owner(ctx):
            await ctx.respond("Nope.", ephemeral=True)
            return

        db = get_db()
        field = field.lower()

        if field == "prestige":
            db.execute(
                "UPDATE players SET prestige_level = ? WHERE user_id = ?",
                (value, target.id)
            )

        elif field == "location":
            if value < 0 or value >= len(LOCATIONS):
                await ctx.respond(
                    f"Location index must be 0–{len(LOCATIONS)-1}.",
                    ephemeral=True
                )
                return

            db.execute(
                "UPDATE players SET location = ? WHERE user_id = ?",
                (LOCATIONS[value]["name"], target.id)
            )

        elif field == "xp":
            db.execute(
                "UPDATE players SET current_xp = ?, total_xp = ? WHERE user_id = ?",
                (value, value, target.id)
            )

        elif field == "cash":
            db.execute(
                "UPDATE players SET cash = ? WHERE user_id = ?",
                (value, target.id)
            )

        else:
            await ctx.respond("Invalid field.", ephemeral=True)
            return

        db.commit()

        await ctx.respond(
            f"Set {field} to {fmt(value)} for {target.name}.",
            ephemeral=True
        )

    # =========================
    # RESET
    # =========================
    @admin.command(name="reset")
    async def reset_player(
        ctx: discord.ApplicationContext,
        target: discord.User
    ):
        if not is_owner(ctx):
            await ctx.respond("Nope.", ephemeral=True)
            return

        db = get_db()

        db.execute(
            """
            UPDATE players
            SET cash = 0,
                sugar = 0,
                yeast = 0,
                moonshine = 0,
                current_xp = 0,
                total_xp = 0,
                prestige_level = 0,
                location = ?
            WHERE user_id = ?
            """,
            (LOCATIONS[0]["name"], target.id)
        )

        db.commit()

        await ctx.respond(
            f"Reset player {target.name}.",
            ephemeral=True
        )
