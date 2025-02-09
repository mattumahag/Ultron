import discord
import os
from discord import *
from discord.ext.commands import has_permissions
from discord.ext import commands
from vars import *

bot = commands.Bot(
    command_prefix=["!", "umahag override -"],
    intents=discord.Intents().all(),
    case_insensitive=True,
)


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="You.")
    )
    await load_cogs()
    print("What is this? What is this place?")


async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            cog_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(cog_name)
                print(f"Loaded {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")


bot.run(TOKEN)
