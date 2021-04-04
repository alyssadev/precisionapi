from .models import Realm, Race, Class, Gender, Guild, GuildRank, Character, ArenaTeam
from .util import get, post
from datetime import datetime

def search(*args, **kwargs):
    return list(_search(*args, **kwargs))

def _search(term):
    results = post("/Characters/ArmorySearch.php", json={"term": term}).json()
    for result in results:
        if result["ResultType"] == "character":
            yield Character.from_search_result(result)
        if result["ResultType"] == "guild":
            yield Guild.from_search_result(result)
        if result["ResultType"] == "arenateam":
            yield ArenaTeam.from_search_result(result)

def get_character(realm: Realm, guid: int):
    character = Character(realm=realm, guid=guid)
    character.populate_data()
    return character
