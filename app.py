import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('TOKEN') # load the token by the os env

bot = commands.Bot(command_prefix='-', description="simple test bot",help_command=None) # you can change the prefix tho

# the presence of the bot
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=f"-help | cuidando el server de kao!"))
    print("bot on")

# simple ping command
@bot.command()
async def ping(ctx):
    await ctx.send("pong")
# help command
@bot.command()
async def help(ctx):
    await ctx.send("""```
-ping: pong
-music: te pone una cancion por el link, pero esta en desarrollo!
-help: muestra el mensaje de ayuda
                   ```""")

bot.run(TOKEN)
