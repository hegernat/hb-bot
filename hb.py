import os
import discord
import asyncio
from dotenv import load_dotenv
from discord.ext import tasks

from db.db import init_db
from db.queries import get_all_active_batches
from game.brewing import resolve_batch_if_needed
from game.utils import fmt

from commands.inventory import register as register_inventory
from commands.buy import register as register_buy
from commands.brew import register as register_brew
from commands.admin import register as register_admin
from commands.sell import register as register_sell
from commands.upgrade import register as register_upgrade
from commands.prestige import register as register_prestige
from commands.leaderboard import register as register_leaderboard
from commands.profile import register as register_profile
from commands.resell import register as register_resell
from commands.protection import register as register_protection
from commands.help import register as register_help
from commands.market import register as register_market

# --- Load environment ---
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN missing from .env")

if not GUILD_ID:
    raise RuntimeError("GUILD_ID missing from .env")


intents = discord.Intents.default()

bot = discord.Bot(intents=intents)


# --- REGISTER COMMANDS (guild scoped explicitly) ---
register_admin(bot, GUILD_ID)
register_inventory(bot, GUILD_ID)
register_buy(bot, GUILD_ID)
register_brew(bot, GUILD_ID)
register_sell(bot, GUILD_ID)
register_resell(bot, GUILD_ID)
register_upgrade(bot, GUILD_ID)
register_prestige(bot, GUILD_ID)
register_leaderboard(bot, GUILD_ID)
register_profile(bot, GUILD_ID)
register_protection(bot, GUILD_ID)
register_help(bot, GUILD_ID)
register_market(bot, GUILD_ID)

@bot.event
async def on_ready():
    print("READY:", bot.user)
    init_db()
    print("Database initialized")

    print("SYNCING...")
    await bot.sync_commands(guild_ids=[GUILD_ID])
    print("SYNC COMPLETE")

    if not check_batches.is_running():
        check_batches.start()



@bot.slash_command(guild_ids=[GUILD_ID], name="ping")
async def ping(ctx):
    await ctx.respond("pong")


@tasks.loop(seconds=20)
async def check_batches():
    await bot.wait_until_ready()

    batches = get_all_active_batches()

    for batch in batches:
        user_id = batch["user_id"]

        result = resolve_batch_if_needed(user_id)

        if not result:
            continue

        try:
            channel_id = batch["channel_id"]
            channel = bot.get_channel(channel_id)

            if not channel:
                continue

            if result["type"] == "complete":
                gained = result["liters"]
                overflow = result.get("overflow", 0)

                message = (
                    f"{channel.guild.get_member(user_id).mention}\n"
                    f"Brew completed\n"
                    f"Liquor added: {fmt(gained)} liters"
                )

                if overflow > 0:
                    message += f"\nStorage overflow: {fmt(overflow)} liters lost"

                await channel.send(message)

            elif result["type"] == "mold":
                await channel.send(
                    f"<@{user_id}>\nBrew failed due to mold."
                )

        except Exception as e:
            print("Alert error:", e)


bot.run(TOKEN)