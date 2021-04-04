import attr
import requests
from datetime import datetime, timedelta

from .variables import API_URL
from .util import retrieve_all_results

class Realm:
    realms = {
        0: "PTR",
        1: "Precision"
    }
    def __init__(self, realm: int):
        self.realm = int(realm)
    def __repr__(self):
        return self.realms[self.realm]

class Race:
    races = {
        1: "Human",
        2: "Orc",
        3: "Dwarf",
        4: "Night Elf",
        5: "Undead",
        6: "Tauren",
        7: "Gnome",
        8: "Troll",
        9: "Goblin",
        10:"Blood Elf",
        11:"Draenei",
        22:"Worgen"
    }
    def __init__(self, race: int):
        self.race = int(race)
    def __repr__(self):
        return self.races[self.race]

class Class:
    classes = {
        1: "Warrior",
        2: "Paladin",
        3: "Hunter",
        4: "Rogue",
        5: "Priest",
        6: "Death Knight",
        7: "Shaman",
        8: "Mage",
        9: "Warlock",
        11: "Druid"
    }
    def __init__(self, class_: int):
        self.class_ = int(class_)
    def __repr__(self):
        return self.classes[self.class_]

class Gender:
    genders = {
        0: "Male",
        1: "Female"
    }
    def __init__(self, gender: int):
        self.gender = int(gender)
    def __repr__(self):
        return self.genders[self.gender]

@attr.s
class PrecisionObject:
    guid: int = attr.ib()
    realm: Realm = attr.ib()

@attr.s
class Guild(PrecisionObject):
    lastupdate: datetime = None
    members: list = None
    def get_members(self, update=False, limit=None):
        if update or not self.members or (
                self.lastupdate and (datetime.now() - self.lastupdate) > timedelta(minutes=30)
            ):
            self.members_raw = retrieve_all_results("/Characters/GetGuildMembers.php", {"guildid": self.guid, "realm": self.realm.realm}, limit=limit)
            self.lastupdate = datetime.now()
            self.members = [
                Character(
                    guid = m["0"],
                    realm = Realm(m["realm"]),
                    lastupdate = self.lastupdate,
                    name = m["1"],
                    level = m["2"],
                    race = Race(m["3"]),
                    gender = Gender(m["4"]),
                    class_ = Class(m["5"]),
                    rank = GuildRank(guild=self, ranklevel=m["6"], rname=m["7"]),
                    offnote = m["8"],
                    pnote = m["9"],
                    guild = self,
                ) for m in self.members_raw
            ]
        return self.members

@attr.s
class GuildRank:
    guild: Guild = attr.ib()
    ranklevel: int = attr.ib()
    rname: str = attr.ib()

@attr.s
class Character(PrecisionObject):
    name: str = attr.ib()
    level: int = attr.ib()
    race: Race = attr.ib()
    gender: Gender = attr.ib()
    class_: Class = attr.ib()
    rank: GuildRank = attr.ib()
    offnote: str = attr.ib()
    pnote: str = attr.ib()
    guild: Guild = attr.ib()
    lastupdate: datetime = attr.ib(default=attr.Factory(datetime.now), repr=False)

@attr.s
class ArenaTeam(PrecisionObject):
    type_: int = attr.ib()
    name: str = attr.ib()
    def __repr__(self):
        return "ArenaTeam(type={0}x{0}, name={1}".format(self.type_, self.name)
