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
        server = ctx.guild
        if args[0] == "add-playlist":
            try:
                _response, _ = y2.create_playlist(args[1], user.name, server.name)
                await ctx.send(_response)
            except:
                await ctx.send("Es probable que no hayas enviado el nombre de la playlist.")
        elif args[0] == "add-video":
            try:
                _response = y2.add_video(args[1], args[2], server.name, user.name)
                await ctx.send(embed=_response)
            except:
                await ctx.send("**Error**: verifica que estás enviando la playlist y la url del video.")
        elif args[0] == "get-playlists":
            data = y2.get_playlists(server.name)
            await ctx.send(embed=data)
        elif args[0] == "get-videos":
            try:
                data, _ = y2.get_videos(args[1], server.name)
                await ctx.send(embed=data)
            except:
                await ctx.send("**Error**: Parece que ha olvidado el nombre de la playlist")
        elif args[0] == "delete-video":
            try:
                embed = y2.delete_video_from_playlist(args[1], server.name, args[2])
                await ctx.send(embed=embed)
            except:
                await ctx.send("**Error:**: Parace que has olvidado el nombre de la playlist o la posición del video. Por favor, verifica.")
        elif args[0] == "delete-playlist":
            try:
                embed = y2.delete_playlist(args[1], server.name)
                await ctx.send(embed=embed)
            except:
                await ctx.send("**Error:**: Parace que has olvidado el nombre de la playlist. Por favor, verifica.")
    else:
        await ctx.send(y2._help())
    
bot.run(TOKEN)
