import discord
import os

import time
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from app.player import RadioPlayer
from app.misc import Misc
# from app.task import BotTask
from app.static import COMMANDS

load_dotenv()

PREFIX = "!eila"
TOKEN = os.getenv("DISCORD_TOKEN")
if os.environ.get("ENVIRONMENT") == "dev":
    PREFIX = "!e"
    TOKEN = os.getenv("DISCORD_TOKEN_DEV")

if TOKEN is None:
    print("CONFIG ERROR: Please state your discord bot token in .env")
    exit()

bot = commands.AutoShardedBot(
    command_prefix=f"{PREFIX} ",
    description="Discord bot untuk memainkan radio favoritmu!",
    help_command=None
)

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")
    print(f"Currently added by {len(bot.guilds)} servers")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"`{PREFIX} help` untuk memulai."))

@bot.command('help')
async def _help(ctx):
    """
    List of commands
    """

    embed = discord.Embed(
        title="Daftar perintah yang tersedia:",
        color=0x9395a5
    )

    for cmd, msg in COMMANDS.items():
        embed.add_field(name=f"{PREFIX} {cmd}", value=f"{msg}", inline=False)

    embed.set_footer(text="radio-id")
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    """Check API latency, bot latency, and reply delay."""
    # Measure API latency to Discord servers
    api_latency = round(bot.latency * 1000, 2)

    # Measure bot latency to Discord servers
    start_time_bot = time.time()
    message_bot = await ctx.send("Pinging Discord servers...")
    end_time_bot = time.time()
    bot_latency = round((end_time_bot - start_time_bot) * 1000, 2)

    # Measure user latency
    start_time_user = time.time()
    async with ctx.typing():  # Use ctx.typing() to trigger a typing indicator
        await asyncio.sleep(0.5)  # Simulate some work to measure user latency
    end_time_user = time.time()
    user_latency = round((end_time_user - start_time_user) * 1000, 2)

    # Calculate reply delay
    reply_delay = round((time.time() - end_time_bot) * 1000, 2)

# Create message
    embed = discord.Embed(title='Pong! 🏓', color=0x3498db)
    embed.add_field(name='API Latency', value=f'{api_latency}ms', inline=False)
    embed.add_field(name='Bot Latency', value=f'{bot_latency}ms', inline=False)
    embed.add_field(name='User Latency', value=f'{user_latency}ms', inline=False)
    embed.add_field(name='Reply Delay', value=f'{reply_delay}ms', inline=False)

    await message_bot.edit(content=None, embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if os.environ.get("ENVIRONMENT") == "dev":
        raise error

    if isinstance(error, commands.CommandOnCooldown):
        cd = "{:.2f}".format(error.retry_after)
        await ctx.send(f"Gunakan command ini lagi setelah {cd} detik")
        return

    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"{str(error)}, use `{PREFIX} help` to list available commands")
        return

    if isinstance(error, commands.ChannelNotFound):
        await ctx.send(str(error))
        return

    if isinstance(error, commands.CommandInvokeError):
        await ctx.send(str(error))
        return

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("MissingRequiredArgument")
        return

    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send(str(error))
        return

    await ctx.send(str(error))
    raise error


bot.add_cog(RadioPlayer(bot, PREFIX))
bot.add_cog(Misc(bot, PREFIX))
# bot.add_cog(BotTask(bot, PREFIX))
bot.run(TOKEN)
