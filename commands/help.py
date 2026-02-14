import discord
from game.utils import fmt


def register(bot, GUILD_ID):

    @bot.slash_command(
        name="help",
        description="Game mechanics and commands etc"
    )
    async def help_command(ctx: discord.ApplicationContext):

        embed = discord.Embed(
            title="HB Game – Help",
            color=0x2f3136
        )

        embed.add_field(
            name="Core Commands",
            value=(
                "/buy – Buy ingredients\n"
                "/brew – Start brewing\n"
                "/sell – Sell moonshine\n"
                "/upgrade – Upgrade location\n"
                "/protection – Upgrade mold/raid protection\n"
                "/prestige – Reset progress for permanent bonuses\n"
                "/inventory – View resources\n"
                "/profile – View XP and prestige progress\n"
                "/leaderboard – Global ranking"
            ),
            inline=False
        )

        embed.add_field(
            name="Brewing",
            value=(
                "• 1 sugar + 1/5 yeast = 5 liters\n"
                "• 1 liter = 1 second base time\n"
                "• Prestige reduces brew time by 5% per level\n"
                "• Mold may destroy a batch before completion"
            ),
            inline=False
        )

        embed.add_field(
            name="Mold",
            value=(
                "• Chance reduced by mold protection\n"
                "• If mold happens:\n"
                "  - Refund based on remaining time\n"
                "  - Minimum 15% refund\n"
                "  - +5% minimum refund per mold tier"
            ),
            inline=False
        )

        embed.add_field(
            name="Raids",
            value=(
                "• Triggered on /sell\n"
                "• Risk increases with prestige and volume sold\n"
                "• Raid protection reduces risk\n"
                "• If raid occurs: lose 50–80% of revenue"
            ),
            inline=False
        )

        embed.add_field(
            name="Prestige",
            value=(
                "• Requires final location\n"
                "• XP requirement increases 5% per prestige level\n"
                "• Resets location + inventory\n"
                "• Sets cash to €500\n"
                "• Keeps total XP\n"
                "• Grants +5% brewing speed per level"
            ),
            inline=False
        )

        embed.add_field(
            name="Protection Cost Scaling",
            value=(
                "Cost scales with:\n"
                "• Protection tier\n"
                "• +50% per location index\n"
                "• +5% per prestige level"
            ),
            inline=False
        )

        await ctx.respond(embed=embed, ephemeral=True)
