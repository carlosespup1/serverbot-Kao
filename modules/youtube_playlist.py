from pymongo import MongoClient
from dotenv import load_dotenv
import os
from enum import Enum
from tabulate import tabulate
from pytube import YouTube
import json
import discord

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
    result = playlists_collection.find({ "server": servername })
    data = []
    for i in result:
        data.append([
            i["name"],
            i["user"]
        ])
    return "```\n" + tabulate(data, headers=["Nombre", "Creada por"], tablefmt="pretty") + "```\n"

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
        return f"La playlist **{playlist}** no existe, por favor, créala para poder usarla."
    try:  # obtener datos del video
        yt = YouTube(url)
        res = json.loads(yt.vid_info["player_response"])
        video_id = res["videoDetails"]["videoId"]
        _videos = _playlist["videos"]
    except:
        return f"El video {url} es inaccesible."
    try:  # Se valida si el video ya existe en la playlist, si no, se guarda,
        founded_video = p_collection.find_one({ "name": playlist, "server": server, "videos.video_id": video_id })
        if founded_video:
            video_user = founded_video["user"]
            return f"El video **{yt.title}** ya existe en **{playlist}**, fue agregado por **{video_user}**"
        p_collection.update(
            { "_id": _playlist["_id"]},
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
        return f"El video **{yt.title}** ha sido agregado correctamente a **{playlist}**"
    except:
        return f"Error al agregar video a **{playlist}**!"

def get_videos(playlist, server = "", db = db):
    p_collection = db.playlists
    _playlist = p_collection.find_one({ "server": server, "name": playlist })
    if not _playlist:
        return discord.Embed(title=f"La playlist **{playlist}** no existe.")
    try:
        videos = _playlist["videos"]
        embed = discord.Embed(title=f"Videos de {playlist}")
        for v in videos:
            _title = v["title"]
            _id = v["position"]
            _url = v["url"]
            _user = v["user"]
            embed.add_field(name=f"**{_title}**", value=f"> Id: {_id}\n> Link: {_url}\n> Agregado por: {_user}", inline=False)
        return embed
    except:
        return discord.Embed(f"Ups! No fue posible obtener los videos de **{playlist}**. Intente más luego.")
