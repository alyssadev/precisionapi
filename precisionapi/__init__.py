from .models import Realm, Race, Class, Gender, Guild, GuildRank, Character, ArenaTeam
from .util import get
from datetime import datetime

def search(term):
    results = post("/Characters/ArmorySearch.php", json={"term": term}).json()
    for result in results:
        if result["ResultType"] == "character":
            yield Character(guid = result["Guid"], realm = Realm(result["Realm"]))

def get_character(realm: Realm, guid: int):
    character = Character(realm=realm, guid=guid)
    character.populate_data()
    return character
