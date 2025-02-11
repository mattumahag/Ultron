import discord
import json
import random
import time
from discord import *
from discord.ext import commands
from discord.ext.commands import has_permissions

# Variables of symbols used for slots
cherries = ":cherries:"
squirts = ":sweat_drops:"
lemon = ":lemon:"
seven = ":seven:"
bell = ":bell:"
grapes = ":grapes:"
eggplant = ":eggplant:"
gem = ":gem:"
coin = ":coin:"
question = ":question:"

symbols = [cherries, squirts, lemon, seven, bell, grapes, eggplant, gem, coin]


# Used to check for user ID in casinoData.jason
def contains_value(json_file, value):
    with open(json_file, "r") as f:
        data = json.load(f)
    return str(value) in data["Users"]


# Generate random symbol for slots
def genSymbol():
    return random.choice(symbols)


# Checks if user has a negative or 0 balance
def hasMoney(user):
    if not contains_value("casinoData.json", user.id):
        return True
    else:
        with open("casinoData.json", "r") as f:
            data = json.load(f)
        if data["Users"][str(user.id)]["Balance"] <= 0:
            return False


# Creates Casino button
class Casino(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    # Slots button
    @discord.ui.button(label="Slots 🎰", style=discord.ButtonStyle.red)
    async def Slots(self, interaction: discord.Interaction, button: discord.ui.Button):

        if hasMoney(interaction.user) == False:
            await interaction.response.send_message("You have 0 dollars!")

        def check(msg):
            return (
                msg.author == interaction.user
                and msg.channel == interaction.channel
                and float(msg.content)
            )

        await interaction.response.defer()
        q = await interaction.followup.send(
            "How much will you bet " + interaction.user.name + "?"
        )

        msg = await self.bot.wait_for("message", check=check)
        bet = float(msg.content)
        await slots(user=interaction.user, bet=bet, channel=interaction.channel)
        time.sleep(2)
        await msg.delete()
        await q.delete()

    @discord.ui.button(label="Blackjack ♠️", style=discord.ButtonStyle.gray)
    async def Blackjack(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):

        if hasMoney(interaction.user) == False:
            await interaction.response.send_message("You have 0 dollars!")

        def check(msg):
                return msg.author == interaction.user and msg.channel == interaction.channel and int(msg.content)
    
        await interaction.response.defer()
        q = await interaction.followup.send("How much will you bet " + interaction.user.name + "?")

        msg = await self.bot.wait_for("message", check=check)
        bet=int(msg.content)
        await blackjack(user=interaction.user, bet=bet, channel=interaction.channel)
        time.sleep(2)
        await msg.delete()
        await q.delete()


async def blackjack(user, bet, channel):
    #Define card deck as set
    card_face= {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14}
    card_suit = {'hearts', 'diamonds', 'clubs', 'spades'}
    deck = [{face, suit} for face in card_face for suit in card_suit]
    random.shuffle(deck)

    player_hand = []
    dealer_hand = []
    
    player_hand.append(deck.pop())
    dealer_hand.append(deck.pop())
    player_hand.append(deck.pop())
    dealer_hand.append(deck.pop())

    

    await channel.send('test')
    print('test')



# Slots game, activated by button in !casino
async def slots(user, bet, channel):
    # Checks if User has data in casinoData, if not uploads data starting with $1000
    with open("casinoData.json") as f:
        data = json.load(f)
    if not contains_value("casinoData.json", user.id):
        data["Users"][str(user.id)] = {"Balance": 1000}
        with open("casinoData.json", "w") as f:
            json.dump(data, f, indent=4)

    userBalance = data["Users"][str(user.id)]["Balance"]

    if userBalance < bet:
        await channel.send(
            f"You don't have enough balance to place a bet of {bet}. Your balance is {userBalance}."
        )
        return

    time.sleep(0.5)

    # Symbol selection
    symbol = genSymbol()
    symbol2 = genSymbol()
    symbol3 = genSymbol()
    slotMSG = await channel.send(f"{symbol} {symbol2} {symbol3}")
    time.sleep(0.5)
    symbol = genSymbol()
    symbol2 = genSymbol()
    symbol3 = genSymbol()
    await slotMSG.edit(content=f"{symbol} {symbol2} {symbol3}")
    time.sleep(0.5)
    symbol = genSymbol()
    symbol2 = genSymbol()
    symbol3 = genSymbol()
    time.sleep(1.2)
    await slotMSG.edit(content=f"{symbol} {symbol2} {symbol3}")

    # Prize calculation
    winningsMax = (bet * 10) + userBalance
    winnings = (bet * 2.5) + userBalance
    smallWinnings = (bet * 1.5) + userBalance
    losings = userBalance - bet

    # Game winning logic
    if symbol == symbol2 == symbol3:
        if symbol == squirts:
            data["Users"][str(user.id)]["Balance"] = winningsMax
            time.sleep(2)
            await channel.send(f"{user.name} won the jackpot!! Balance: {winningsMax}")
        else:
            data["Users"][str(user.id)]["Balance"] = winnings
            time.sleep(2)
            await channel.send(f"{user.name} won! Balance: {winnings}")
    else:
        if symbol == symbol2 or symbol2 == symbol3 or symbol == symbol3:
            data["Users"][str(user.id)]["Balance"] = smallWinnings
            time.sleep(2)
            await channel.send(f"{user.name} won! Balance: {smallWinnings}")
        else:
            data["Users"][str(user.id)]["Balance"] = losings
            time.sleep(2)
            await channel.send(f"{user.name} lost! Balance: {losings}")

    with open("casinoData.json", "w") as f:
        json.dump(data, f, indent=4)


class casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Creates casino embed, allows user to select game
    @commands.command()
    async def casino(self, ctx):
        embed = discord.Embed(title="Casino", description="Click on a game below")
        embed.add_field(
            name="Slots", value="Spin three Squirt's in a row to win!", inline=False
        )
        embed.add_field(
            name="Blackjack",
            value="Closest to 21 without going over wins!",
            inline=False,
        )
        # embed.add_field(name='!', value='', inline=False)
        # embed.add_field(name='!', value='', inline=False)
        view = Casino(self.bot)
        await ctx.send(embed=embed, view=view)

    # Check user balance
    @commands.command()
    async def balance(self, ctx, member: discord.Member = None):
        if member is None:
            user = ctx.author
        else:
            user = member
        with open("casinoData.json", "r") as f:
            data = json.load(f)
        if not contains_value("casinoData.json", user.id):
            await ctx.send(f"{member} has not played any casino games!")
        else:
            await ctx.send(
                "You have $" + str(data["Users"][str(user.id)]["Balance"]) + "!"
            )

    # Admin command: Add money to user
    @commands.command()
    async def addMoney(self, ctx, amount: float = None, member: discord.Member = None):
        if ctx.author.id == 239116660592738304 or 722251013784076321:
            if amount is None:
                ctx.send("Specify an amount to add.")
            if member is None:
                user = ctx.author
            else:
                user = member

            with open("casinoData.json", "r") as f:
                data = json.load(f)
            if not contains_value("casinoData.json", user.id):
                await ctx.send(f"{member} has not played any casino games!")
            else:
                data["Users"][str(user.id)]["Balance"] += amount
                with open("casinoData.json", "w") as f:
                    json.dump(data, f, indent=4)
                await ctx.send(
                    "$"
                    + str(amount)
                    + " has been added! New balance: "
                    + str(data["Users"][str(user.id)]["Balance"])
                )


async def setup(bot):
    await bot.add_cog(casino(bot))
