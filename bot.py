import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# ============================================================
# CONFIG
# ============================================================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN staat niet in je .env bestand.")


# ============================================================
# INTENTS
# ============================================================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ============================================================
# NAMES
# ============================================================

ROLES = [
    "👑elite👑",
    "📩ticket helper📩",
    "👑owner👑",
]


# ============================================================
# CHANNEL PERMISSIONS
# ============================================================

def public_permissions():
    """
    Normal public channel.
    Iedereen kan kijken en praten.
    """
    return {
        "view_channel": True,
        "send_messages": True,
        "read_message_history": True,
    }


def website_only_permissions():
    """
    Kanalen die bedoeld zijn om via de website gebruikt te worden.

    De bot stuurt hier GEEN berichten en heeft GEEN
    ticket/website functionaliteit.
    """
    return {
        "view_channel": True,
        "send_messages": False,
        "read_message_history": True,
    }


# ============================================================
# SETUP COMMAND
# ============================================================

@bot.tree.command(
    name="setup",
    description="Creates the complete Elite Client Discord server structure."
)
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction):

    guild = interaction.guild

    if guild is None:
        await interaction.response.send_message(
            "This command can only be used inside a server.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    # --------------------------------------------------------
    # ROLES
    # --------------------------------------------------------

    created_roles = {}

    for role_name in ROLES:

        existing_role = discord.utils.get(
            guild.roles,
            name=role_name
        )

        if existing_role:
            created_roles[role_name] = existing_role
        else:
            role = await guild.create_role(
                name=role_name,
                reason="Elite Client server setup"
            )

            created_roles[role_name] = role

    # --------------------------------------------------------
    # CATEGORIES
    # --------------------------------------------------------

    info_category = discord.utils.get(
        guild.categories,
        name="INFO"
    )

    if info_category is None:
        info_category = await guild.create_category(
            "INFO",
            reason="Elite Client server setup"
        )

    tickets_category = discord.utils.get(
        guild.categories,
        name="TICKETS"
    )

    if tickets_category is None:
        tickets_category = await guild.create_category(
            "TICKETS",
            reason="Elite Client server setup"
        )

    public_category = discord.utils.get(
        guild.categories,
        name="PUBLIC"
    )

    if public_category is None:
        public_category = await guild.create_category(
            "PUBLIC",
            reason="Elite Client server setup"
        )

    # --------------------------------------------------------
    # INFO CHANNELS
    # --------------------------------------------------------

    info_channels = [
        "announcements",
        "updates",
        "rules",
        "polls",
        "giveaway",
    ]

    for channel_name in info_channels:

        existing = discord.utils.get(
            guild.text_channels,
            name=channel_name
        )

        if existing is None:
            await guild.create_text_channel(
                channel_name,
                category=info_category,
                reason="Elite Client server setup"
            )

    # --------------------------------------------------------
    # TICKET CHANNELS
    # --------------------------------------------------------

    ticket_channels = [
        "create-a-ticket",
        "ai-ticket",
    ]

    for channel_name in ticket_channels:

        existing = discord.utils.get(
            guild.text_channels,
            name=channel_name
        )

        if existing is None:
            channel = await guild.create_text_channel(
                channel_name,
                category=tickets_category,
                reason="Elite Client server setup"
            )

            # No messages / no normal usage.
            # These channels are only placeholders for the
            # website / future functionality.

            await channel.set_permissions(
                guild.default_role,
                send_messages=False
            )

    # --------------------------------------------------------
    # PUBLIC TEXT CHANNELS
    # --------------------------------------------------------

    public_text_channels = [
        "general",
        "review",
    ]

    for channel_name in public_text_channels:

        existing = discord.utils.get(
            guild.text_channels,
            name=channel_name
        )

        if existing is None:

            channel = await guild.create_text_channel(
                channel_name,
                category=public_category,
                reason="Elite Client server setup"
            )

            # Reviews are website-only.
            if channel_name == "review":
                await channel.set_permissions(
                    guild.default_role,
                    send_messages=False
                )

    # --------------------------------------------------------
    # PUBLIC FORUMS
    # --------------------------------------------------------

    # Suggestions forum
    existing_suggestions = discord.utils.get(
        guild.forums,
        name="suggestions"
    )

    if existing_suggestions is None:

        await guild.create_forum(
            "suggestions",
            category=public_category,
            reason="Elite Client server setup"
        )

    # Bugs forum
    existing_bugs = discord.utils.get(
        guild.forums,
        name="bugs"
    )

    if existing_bugs is None:

        await guild.create_forum(
            "bugs",
            category=public_category,
            reason="Elite Client server setup"
        )

    # --------------------------------------------------------
    # DONE
    # --------------------------------------------------------

    await interaction.followup.send(
        "Elite Client server setup completed.",
        ephemeral=True
    )


# ============================================================
# ERROR HANDLING
# ============================================================

@setup.error
async def setup_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):

    if isinstance(error, app_commands.MissingPermissions):

        if not interaction.response.is_done():
            await interaction.response.send_message(
                "You need Administrator permission to use /setup.",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                "You need Administrator permission to use /setup.",
                ephemeral=True
            )

        return

    raise error


# ============================================================
# READY
# ============================================================

@bot.event
async def on_ready():

    try:
        synced = await bot.tree.sync()

        print(
            f"Logged in as {bot.user}"
        )

        print(
            f"Synced {len(synced)} slash command(s)."
        )

    except Exception as e:
        print(
            f"Failed to sync commands: {e}"
        )


# ============================================================
# START
# ============================================================

bot.run(TOKEN)
