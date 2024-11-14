import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import datetime

# Load environment variables from .env file
load_dotenv()

# Get bot token and other settings from the .env file
TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_ID = int(os.getenv("SERVER_ID"))
LOGGING_CHANNEL_ID = int(os.getenv("LOGGING_CHANNEL_ID"))
OWNER_ID = int(os.getenv("OWNER_ID"))

intents = discord.Intents.default()
intents.members = True  # Ensure the bot has member intents enabled
bot = commands.Bot(command_prefix="!", intents=intents)

# Add the owner commands cog
from owner_commands import bot as owner_bot
bot.add_cog(owner_bot)

# Log messages in the specified logging channel
async def log_to_channel(message):
    guild = bot.get_guild(SERVER_ID)
    channel = guild.get_channel(LOGGING_CHANNEL_ID)
    if channel:
        await channel.send(message)

# Handle bot startup
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await log_to_channel(f'{bot.user} has connected to Discord!')
    await bot.tree.sync()  # Sync the slash commands

# Track users with the "unverified" role
user_timestamps = {}

@bot.event
async def on_member_update(before, after):
    # Check if the "unverified" role has been added to a user
    unverified_role = discord.utils.get(after.guild.roles, name="unverified")
    
    if unverified_role in after.roles and unverified_role not in before.roles:
        # Role was assigned, store the timestamp
        user_timestamps[after.id] = datetime.datetime.utcnow()

# Periodically check users with the "unverified" role
@tasks.loop(hours=24)  # Runs once a day
async def check_unverified_users():
    for user_id, timestamp in list(user_timestamps.items()):
        user = await bot.fetch_user(user_id)
        time_passed = datetime.datetime.utcnow() - timestamp
        
        if time_passed > datetime.timedelta(weeks=1):
            # Get the server and the "unverified" role
            guild = user.guild
            unverified_role = discord.utils.get(guild.roles, name="unverified")
            
            if unverified_role in user.roles:
                # Remove the role and kick the user
                await user.remove_roles(unverified_role)
                await user.kick(reason="Unverified for over a week")
                await log_to_channel(f"Kicked {user.name} for being unverified for over a week.")
                del user_timestamps[user_id]

@bot.command()
async def add_unverified(ctx, member: discord.Member):
    """Command to manually add the unverified role for testing."""
    unverified_role = discord.utils.get(ctx.guild.roles, name="unverified")
    if unverified_role:
        await member.add_roles(unverified_role)
        user_timestamps[member.id] = datetime.datetime.utcnow()
        await ctx.send(f"{member.mention} has been marked as unverified.")

# Start checking unverified users
check_unverified_users.start()

# Run the bot
bot.run(TOKEN)
