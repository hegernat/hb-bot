import discord


def register(bot):

    @bot.slash_command(
        name="help",
        description="Game mechanics and commands"
    )
    async def help_command(ctx: discord.ApplicationContext):

        embed = discord.Embed(
            title="HomeBurner — Game Guide",
            color=0x2f3136
        )

        # -------------------------------------------------
        # Core Commands
        # -------------------------------------------------
        embed.add_field(
            name="Core Commands",
            value=(
                "/buy – Buy sugar & yeast\n"
                "/brew [amount] – Start brewing (e.g. 5000, 5k, all)\n"
                "/sell – Sell to a market buyer\n"
                "/resell – Resell your ingredients\n"
                "/market – View current buyers & heat level\n"
                "/upgrade – Upgrade location\n"
                "/protection – Upgrade mold/raid protection\n"
                "/inventory – View resources & heat\n"
                "/profile – View XP & prestige\n"
                "/prestige – Reset progress for permanent bonus\n"
                "/leaderboard – Global ranking"
            ),
            inline=False
        )

        # -------------------------------------------------
        # Brewing
        # -------------------------------------------------
        embed.add_field(
            name="Brewing",
            value=(
                "• 5 sugar + 1 yeast = 5 liters liquor\n"
                "• 1 liter = 1 second base time\n"
                "• /brew all fills remaining storage automatically\n"
                "• Prestige reduces brew time by 5% per level\n"
                "• Mold can ruin a batch before completion"
            ),
            inline=False
        )

        # -------------------------------------------------
        # Mold
        # -------------------------------------------------
        embed.add_field(
            name="Mold System",
            value=(
                "• Base mold risk applies per batch\n"
                "• Mold protection reduces failure chance\n"
                "• If mold occurs:\n"
                "  - Partial refund based on time remaining\n"
                "  - Minimum 15% refund\n"
                "  - +5% minimum refund per mold tier"
            ),
            inline=False
        )

        # -------------------------------------------------
        # Market & Heat
        # -------------------------------------------------
        embed.add_field(
            name="Market & Heat",
            value=(
                "• Market refreshes every hour\n"
                "• 3 buyers per location with different volume & risk\n"
                "• Selling increases Heat (based on volume sold)\n"
                "• Higher Heat = higher raid risk\n"
                "• Heat resets each hour and on prestige"
            ),
            inline=False
        )

        # -------------------------------------------------
        # Raids
        # -------------------------------------------------
        embed.add_field(
            name="Raids",
            value=(
                "• Raid chance = Buyer risk × Heat × XP scaling\n"
                "• Raid protection reduces money lost (not risk)\n"
                "• If raided:\n"
                "  - Lose a % of revenue\n"
                "  - XP is based on actual money received"
            ),
            inline=False
        )

        # -------------------------------------------------
        # Prestige
        # -------------------------------------------------
        embed.add_field(
            name="Prestige",
            value=(
                "• Requires final location + required XP\n"
                "• XP requirement increases 5% per prestige level\n"
                "• Resets inventory, location & protection\n"
                "• Clears Heat\n"
                "• Grants +5% permanent brewing speed per level"
            ),
            inline=False
        )

        await ctx.respond(embed=embed, ephemeral=True)