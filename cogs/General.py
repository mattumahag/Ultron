import discord
import random
import nacl
from vars import *
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Check User Ping Command
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}ms")

    # Guessing game 1-10
    @commands.command()
    async def game(self, ctx):
        computer = random.randint(1, 10)
        await ctx.send("Guess my number")

        def check(msg):
            return (
                msg.author == ctx.author
                and msg.channel == ctx.channel
                and int(msg.content) in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            )

        msg = await self.bot.wait_for("message", check=check)

        if int(msg.content) == computer:
            await ctx.send("Good job :skull:")
        else:
            quote = random.randint(1, 3)
            if quote == 1:
                await ctx.send(avengers_extinction + " (" + str(computer) + ")")
            else:
                if quote == 2:
                    await ctx.send(god + " (" + str(computer) + ")")
                else:
                    if quote == 3:
                        await ctx.send(rich + " (" + str(computer) + ")")

    @commands.command()
    async def kishan(self, ctx):
        await ctx.send("Kishan Gunawardana is a bitch I fuck his dad")

    @commands.command()
    async def prison(self, ctx):
        await ctx.send(
            "Kishan's dad went to federal prison on 10/12/2001 after he was found and caught by the FBI and went on trial for the 9/11 Bombings. He was also the suspect in numerous rape, sexual assault, sex trafficking, statutory rape, pedophilia, murder and abuse cases filed by his ex-wife and son, Kishan Gunawardana. He will serve a life sentence and is not allowed visitors for his actions."
        )

    # Makes the bot join the vc
    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice.channel is None:
            await ctx.send("You're not in a voice channel!")
            return

        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()

    # Makes the bot leave the vc
    @commands.command()
    async def leave(self, ctx):
        voice = ctx.voice_client
        await voice.disconnect()

    # Kicks a specified user from the voice channel
    @commands.command()
    async def kick(self, ctx, user: discord.Member):
        await user.move_to(None)

    # List out all available commands
    @commands.command()
    async def commands(self, ctx):
        embed = discord.Embed(
            title="Command List", description="List of commands and what they do."
        )
        embed.add_field(
            name="!gpa",
            value="Calculates your GPA when you input your grades.",
            inline=False,
        )
        embed.add_field(
            name="!game",
            value="I will pick a random number from 1-10. If you guess it right you win.",
            inline=False,
        )
        embed.add_field(name="ping", value="Sends back your ping.", inline=False)
        embed.add_field(name="!peacekeep", value="", inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))
