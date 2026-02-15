import discord
import time

from db.queries import get_player, get_exposure
from game.locations import LOCATIONS, get_location_index
from game.market import generate_market
from game.utils import fmt

def register(bot):

    @bot.slash_command(
        name="market",
        description="View current buyers"
    )
    async def market(ctx: discord.ApplicationContext):

        user_id = ctx.author.id
        player = get_player(user_id)

        if not player:
            await ctx.respond(
                "You don't have a profile yet.",
                ephemeral=True
            )
            return

        # -------------------------------------------------
        # Location + Market
        # -------------------------------------------------
        location_index = get_location_index(player["location"])
        offers = generate_market(location_index)
        max_storage = LOCATIONS[location_index]["max_storage"]

        # -------------------------------------------------
        # Exposure / Heat
        # -------------------------------------------------
        current_hour = int(time.time() // 3600)
        exposure = get_exposure(user_id, current_hour)

        heat_ratio = exposure / max_storage if max_storage > 0 else 0
        heat_percent = int(heat_ratio * 100)

        # Heat status tiers
        if heat_percent < 25:
            heat_status = "Low Profile"
        elif heat_percent < 50:
            heat_status = "Warming Up"
        elif heat_percent < 75:
            heat_status = "Police Attention Rising"
        elif heat_percent < 100:
            heat_status = "High Risk"
        else:
            heat_status = "WANTED!"

        # Clamp for display only
        display_percent = min(heat_percent, 100)

        # Visual bar
        bar_length = 10
        filled = int(min(heat_ratio, 1) * bar_length)
        heat_bar = "█" * filled + "░" * (bar_length - filled)

        # -------------------------------------------------
        # Embed
        # -------------------------------------------------
        embed = discord.Embed(
            title="HB — Current Market",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="Heat Level",
            value=f"{heat_status}\n{heat_bar} {display_percent}%{'+' if heat_percent > 100 else ''}\n\n",
            inline=False
        )

        for offer in offers:
            embed.add_field(
                name=f"#{offer['slot']} — {offer['name']}",
                value=(
                    f"Wants: {fmt(offer['volume_min'])}–"
                    f"{fmt(offer['volume_max'])} L\n"
                    f"Price: €{offer['price_per_liter']}/L\n"
                    f"Base raid risk: {int(offer['base_raid']*100)}%"
                ),
                inline=False
            )

        # -------------------------------------------------
        # Market Timer
        # -------------------------------------------------
        seconds_remaining = 3600 - (int(time.time()) % 3600)
        minutes = seconds_remaining // 60

        embed.set_footer(
            text=f"Market refreshes in {minutes} minutes"
        )

        await ctx.respond(embed=embed)