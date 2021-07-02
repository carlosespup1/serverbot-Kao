from pymongo import MongoClient
from dotenv import load_dotenv
import os
from enum import Enum
from tabulate import tabulate

load_dotenv()
MONGO_HOST = os.getenv('MONGO_HOST') # ADD "mongodb://localhost:27017" in your local .env file
DBNAME = os.getenv('DBNAME')

client = MongoClient(MONGO_HOST)
db = client[DBNAME]

# Playlist collection struct
# {
#     id: ObjectDd(),
#     name: "playlist_name",
#     user: "username",
#     server: "servername"
# }

# To manage playlist creation states
class PlaylistEnum(Enum):
    ALREADY_EXISTS = 0
    CREATED = 1
    CREATION_ERROR = 2

def create_playlist(playlist, username, servername = "", db=db):
    """
    Create playlist in MongoDB
    playlist: Playlist name
    username: Who create playlist
    servername: Server associated with
    """
    playlists_collection = db.playlists
    result = playlists_collection.find({ "name": playlist })
    if result.count() > 0:
        return PlaylistEnum.ALREADY_EXISTS
    created = playlists_collection.insert_one({
        "name": playlist,
        "user": username,
        "server": servername
    })
    if created:
        return PlaylistEnum.CREATED
    return PlaylistEnum.CREATION_ERROR


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
    `y2_playlist add-video <playlist> <videourl>`
    Se debe tener en consideración que la playlist debe estar creada.

    **Para obtener la lista de playlist
    Ejecute: 
    `-y2_playlist get-playlists`
    """ 
