from discord import app_commands
from discord.ext import commands
import os
import sys

# Bot owner ID (replace with your own Discord user ID)
OWNER_ID = 123456789012345678  # Change this to your Discord ID

# Define the command prefix and bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default(), application_id=YOUR_APPLICATION_ID)

# Check if the author is the bot owner
def is_owner(ctx):
    return ctx.author.id == OWNER_ID

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Sync the commands to Discord when the bot is ready
    await bot.tree.sync()

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    """Ping command to check if the bot is responsive."""
    await interaction.response.send_message("Pong!")

@bot.tree.command(name="restart")
async def restart(interaction: discord.Interaction):
    """Restart the bot."""
    if is_owner(interaction):
        await interaction.response.send_message("Restarting bot...")
        os.execv(sys.executable, ['python'] + sys.argv)  # Restart the bot
    else:
        await interaction.response.send_message("You don't have permission to use this command.")

@bot.tree.command(name="shutdown")
async def shutdown(interaction: discord.Interaction):
    """Shutdown the bot."""
    if is_owner(interaction):
        await interaction.response.send_message("Shutting down bot...")
        await bot.close()
    else:
        await interaction.response.send_message("You don't have permission to use this command.")

@bot.tree.command(name="say")
async def say(interaction: discord.Interaction, message: str):
    """Bot says the provided message."""
    if is_owner(interaction):
        await interaction.response.send_message(message)
    else:
        await interaction.response.send_message("You don't have permission to use this command.")
