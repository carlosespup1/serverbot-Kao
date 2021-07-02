import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import modules.youtube_playlist as y2

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
    user = ctx.author
    print(user.name)
    await ctx.send("pong")
# help command
@bot.command()
async def help(ctx):
    await ctx.send("""```
-ping: pong
-music: te pone una cancion por el link, pero esta en desarrollo!
-help: muestra el mensaje de ayuda
                   ```""")

@bot.command(name="y2_playlist")
async def y2_playlist(ctx, *args):
    if len(args) > 0:
        user = ctx.author
        if args[0] == "add-playlist":
            try:
                _response = y2.create_playlist(args[1], user.name)
                if _response == y2.PlaylistEnum.CREATED:
                    await ctx.send(f"Playlist **{args[1]}** creada con éxito por **{user.name}**")
                elif _response == y2.PlaylistEnum.ALREADY_EXISTS:
                    await ctx.send(f"Playlist **{args[1]}** ya existe.")
                else:
                    await ctx.send("*Ups!* No se pudo crear, intente más luego.")
            except:
                await ctx.send("Es probable que no hayas enviado el nombre de la playlist.")
    else:
        await ctx.send(y2._help())
    
bot.run(TOKEN)
