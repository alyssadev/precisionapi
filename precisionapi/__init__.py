from .models import Realm, Race, Class, Gender, Guild, GuildRank, Character, ArenaTeam, Progression
from .models import PrecisionRealmObject as _pro
from .util import get, post
from datetime import datetime

def search(term, filter: _pro=None):
    results = post("/Characters/ArmorySearch.php", json={"term": term}).json()
    out = []
    for result in results:
        if result["ResultType"] == "character":
            out.append(Character.from_search_result(result))
        if result["ResultType"] == "guild":
            out.append(Guild.from_search_result(result))
        if result["ResultType"] == "arenateam":
            out.append(ArenaTeam.from_search_result(result))
    if filter:
        out = [r for r in out if type(r) is filter]
    return out

def find(term, cls: _pro):
    results = search(term, filter=cls)
    if len(results) != 1:
        return results
    return results[0]

def get_character(realm: Realm, guid: int):
    character = Character(realm=realm, guid=guid)
    character.populate_data()
    return character

def get_guild(realm: Realm, guid: int):
    guild = Guild(realm=realm, guid=guid)
    guild.populate_data()
    return guild
