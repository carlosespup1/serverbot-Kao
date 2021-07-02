from pymongo import MongoClient
from dotenv import load_dotenv
import os
from enum import Enum

load_dotenv()
MONGO_HOST = os.getenv('MONGO_HOST') # ADD "mongodb://localhost:27017" in your local .env file
DBNAME = os.getenv('DBNAME')

client = MongoClient(MONGO_HOST)
db = client[DBNAME]

# To manage playlist creation states
class PlaylistEnum(Enum):
    ALREADY_EXISTS = 0
    CREATED = 1
    CREATION_ERROR = 2

def create_playlist(playlist, username, db=db):
    playlists_collection = db.playlists
    result = playlists_collection.find({ "name": playlist })
    if result.count() > 0:
        return PlaylistEnum.ALREADY_EXISTS
    created = playlists_collection.insert_one({
        "name": playlist,
        "user": username
    })
    if created:
        return PlaylistEnum.CREATED
    return PlaylistEnum.CREATION_ERROR


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
    """ 


