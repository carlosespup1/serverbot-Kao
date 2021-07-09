from emoji.core import emojize
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from enum import Enum
from tabulate import tabulate
from pytube import YouTube
import json
import discord
import emoji

load_dotenv()
MONGO_HOST = os.getenv('MONGO_HOST') # ADD "mongodb://localhost:27017" in your local .env file
DBNAME = os.getenv('DBNAME')

client = MongoClient(MONGO_HOST)
db = client[DBNAME]

# Playlist collection struct
# {
#     id: ObjectId(),
#     name: string,
#     user: string,
#     server: string,
#     videos: [videos...]
# }
# Video collection struct
# {
#     position : int
#     title: string,
#     url: string,
#     user: string,
#     video_id: youtube_id
# }

# To manage playlist creation states
class PlaylistEnum(Enum):
    ALREADY_EXISTS = 0
    CREATED = 1
    CREATION_ERROR = 2

class VideosEnum(Enum):
    PLAYLIST_DOESNT_EXISTS = 0
    OK = 1 # playlist exists, with content or not
    DB_ERROR = 2

def create_playlist(playlist, username, servername = "", db=db):
    """
    Create playlist in MongoDB
    Return message and enum
    playlist: Playlist name
    username: Who create playlist
    servername: Server associated with
    """
    playlists_collection = db.playlists
    result = playlists_collection.find({ "name": playlist, "server": servername })
    if result.count() > 0:
        return f"Playlist **{playlist}** ya existe.", PlaylistEnum.ALREADY_EXISTS
    created = playlists_collection.insert_one({
        "name": playlist,
        "user": username,
        "server": servername,
        "videos": []
    })
    if created:
        return f"Playlist **{playlist}** creada con éxito por **{username}**", PlaylistEnum.CREATED
    return "*Ups!* No se pudo crear, intente más luego.", PlaylistEnum.CREATION_ERROR


def get_playlists(servername, db = db):
    """
    Return str with formated table with information.
    servername: Where playlists is associated
    """
    playlists_collection = db.playlists
    result = list(playlists_collection.find({ "server": servername }))
    if len(result) == 0:
        return discord.Embed(description="No existen playlists creadas.")
    embed = discord.Embed(title="Playlists")
    for i in result:
        _name = i["name"]
        _user = i["user"]
        embed.add_field(name=_name, value=f"> Creada por: {_user}", inline=False)
    return embed

def _help():
    return """
    **Y2 Playlist Command**
    Este comando es usado para crear playlists de videos de Youtube. 

    **Para crear una nueva playlist**
    Ejecute:
    `-y2_playlist add-playlist <nombre>`
    Se debe tener en consideración que no pueden repetirse los nombres de las playlist.

    **Para agregar videos**
    Ejecute:
    `-y2_playlist add-video <playlist> <videourl>`
    Se debe tener en consideración que la playlist debe estar creada.

    **Para obtener la lista de playlist**
    Ejecute: 
    `-y2_playlist get-playlists`

    **Para obtener la lista de los videos de una playlist**
    Ejecute
    `-y2_playlist get-videos <playlist>`

    **Para eliminar un video de una playlist**
    Ejecute
    `-y2_playlist delete-video <playlist> <position>`
    
    **Para eliminar una playlist**
    Ejecute
    `-y2_playlist delete-playlist <playlist>`
    
    **Para renombrar una playlist**
    Ejecute
    `-y2_playlist rename <actual_name> <new_name>`

    """ 

def add_video(playlist, url, server = "", user = "", db = db):
    """
    Update playlist videos list with new video.
    playlist: playlist name
    url: YouTube video url
    server: server name associated with playlist
    user: user who invoke command
    """
    p_collection = db.playlists
    _playlist = p_collection.find_one({ "server": server, "name": playlist })
    if not _playlist:  # Validar si existe playlist
        return discord.Embed(description=f"La playlist **{playlist}** no existe, por favor, créala para poder usarla.")
    try:  # obtener datos del video
        yt = YouTube(url)
        res = json.loads(yt.vid_info["player_response"])
        video_id = res["videoDetails"]["videoId"]
        _videos = _playlist["videos"]
    except:
        return discord.Embed(description=f"El video {url} es inaccesible.")
    try:  # Se valida si el video ya existe en la playlist, si no, se guarda,
        founded_video = p_collection.find_one({ "name": playlist, "server": server, "videos.video_id": video_id })
        if founded_video:
            video_user = founded_video["user"]
            return discord.Embed(description=f"El video **{yt.title}** ya existe en **{playlist}**, fue agregado por **{video_user}**")
        p_collection.update(
            { "_id": _playlist["_id"] },
            {
                '$push': {
                    'videos': {
                        'position': len(_videos) + 1,
                        'title': yt.title,
                        'url': url,
                        'user': user,
                        'video_id':  video_id
                    }
                }
            }
        )
        return discord.Embed(description=f"El video **{yt.title}** ha sido agregado correctamente a **{playlist}**")
    except:
        return discord.Embed(description=f"Error al agregar video a **{playlist}**!")

def get_videos(playlist, server = "", db = db):
    """
    Get videos from playlist.
    playlist: playlist name
    server: server name associated with playlist
    Return: Embed discord object and None if playlist doesn´t exist or error, or video list
    """
    p_collection = db.playlists
    _playlist = p_collection.find_one({ "server": server, "name": playlist })
    if not _playlist:
        return discord.Embed(description=f"La playlist **{playlist}** no existe."), { "status": VideosEnum.PLAYLIST_DOESNT_EXISTS, "videos": None}
    try:
        videos = _playlist["videos"]
        if len(videos) == 0:
            return discord.Embed(description=f"No existen videos en **{playlist}**"), { "status": VideosEnum.OK, "videos": videos }
        embed = discord.Embed(title=f"Videos de {playlist}")
        for v in videos:
            _title = v["title"]
            _id = v["position"]
            _url = v["url"]
            _user = v["user"]
            embed.add_field(name=f"**{_title}**", value=f"> Pos: {_id}\n> Link: {_url}\n> Agregado por: {_user}", inline=False)
        return embed, { "status": VideosEnum.OK, "videos": videos }
    except:
        return discord.Embed(f"Ups! No fue posible obtener los videos de **{playlist}**. Intente más luego."), { "status": VideosEnum.DB_ERROR, "videos": None }

def delete_video_from_playlist(playlist, server, position, db=db):
    """
    Delete video from playlist given position
    playlist: Playlist name
    server: server name
    position: Video position in the playlist
    """
    p_collection = db.playlists
    _playlist = p_collection.find_one({ "server": server, "name": playlist })
    embed, res = get_videos(playlist, server, db = db)
    if res["videos"] is None and VideosEnum.PLAYLIST_DOESNT_EXISTS:
        return embed
    if res["videos"] is None and VideosEnum.DB_ERROR:
        return embed
    if not str(position).isdigit():
        return discord.Embed(description=f"Recuerda que se debe identificar el video a eliminar con el número de su posición.")
    if len(res["videos"]) < int(position):
        mess = emoji.emojize("IndexOfOutArray amiguito :grimacing:")
        return discord.Embed(description=mess)
    pos = int(position)
    videos = res["videos"]
    try:
        for i in videos:
            if i["position"] > pos:
                i["position"] -= 1
        d_title = videos.pop(pos - 1)["title"]
        p_collection.update(
            { "_id": _playlist["_id"] },
            {
                '$set': {
                    'videos': videos
                }
            }
        )
    except:
        return discord.Embed(description="Algo salió mal :(")
    return discord.Embed(description=emoji.emojize(f"El video *{d_title}* ha sido eliminado exitosamente :scream_cat:."))

def delete_playlist(playlist, servername, db = db):
    p_collection = db.playlists
    _playlist = p_collection.find_one({ "server": servername, "name": playlist })
    if not _playlist:
        return discord.Embed(description=f"La playlist **{playlist}** no existe.")
    name = _playlist["name"]
    try:
        p_collection.delete_one({ "_id": _playlist["_id"] })
        return discord.Embed(description=emoji.emojize(f"La playlist **{name}** se ha eliminado exitosamente :scream_cat:."))
    except Exception as e:
        return discord.Embed(description="**Error**: Ha ocurrido un error al eliminar la playlist :(")

def update_playlist_name(playlist, servername, new_name, user_name, db = db):
    p_collection = db.playlists
    _playlist = p_collection.find_one({ "server": servername, "name": playlist })
    if not _playlist:
        return discord.Embed(title=f"La playlist **{playlist}** no existe.")
    try:
        _user = _playlist["user"]
        if user_name == _playlist["user"]:
            p_collection.update(
                { "_id": _playlist["_id"] },
                {
                    "$set": {
                        "name": new_name
                    }
                }
            )
            return discord.Embed(description="Nombre actualizado correctamente.")
        return discord.Embed(description=f"Solo el usuario que creó la playlist puede renombrar la playlist (@{_user})")
    except:
        return discord.Embed(description="**Error**: Ha ocurrido un error al actualizar el nombre de la playlist :(")


create_playlist("playlist", "other", "Tortuga Coder")