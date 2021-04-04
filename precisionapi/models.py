import attr
import requests
from datetime import datetime, timedelta
import typing

from .variables import API_URL
from .util import retrieve_all_results, get

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
class Specialization:
    name: str = attr.ib()
    count: int = attr.ib()
    mainspec: bool = attr.ib()
    def __repr__(self):
        return f"{self.name}: {self.count}, {'Main' if self.mainspec else 'Off'}"
    @staticmethod
    def from_armory(data, mainspec: bool):
        return Specialization(data["TalentGroupName"], data["TalentCount"], mainspec)

@attr.s
class Profession:
    profession: str = attr.ib()
    value: int = attr.ib()
    def __repr__(self):
        return f"{self.profession} ({self.value})"

@attr.s
class Item:
    guid: int = attr.ib()
    name: str = attr.ib()
    slot: int = attr.ib(default=None)

@attr.s
class PrecisionObject:
    guid: int = attr.ib()

@attr.s
class PrecisionRealmObject(PrecisionObject):
    realm: Realm = attr.ib()

@attr.s
class Account(PrecisionObject):
    name: str = attr.ib(default=None)

@attr.s
class Guild(PrecisionRealmObject):
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

    @staticmethod
    def from_search_result(result):
        return Guild(
            guid = result["Id"],
            realm = Realm(result["Realm"]),
            name = result["Name"]
        )

@attr.s
class GuildRank:
    guild: Guild = attr.ib()
    ranklevel: int = attr.ib()
    rname: str = attr.ib()

@attr.s
class Character(PrecisionRealmObject):
    name: str = attr.ib(default=None)
    level: int = attr.ib(default=None)
    account: Account = attr.ib(default=None, repr=False)
    gm: bool = attr.ib(default=None, repr=False)
    money: int = attr.ib(default=None, repr=False)
    race: Race = attr.ib(default=None, repr=False)
    gender: Gender = attr.ib(default=None, repr=False)
    class_: Class = attr.ib(default=None)
    achievement_points: int = attr.ib(default=None, repr=False)
    professions: typing.List[Profession] = attr.ib(default=None, repr=False)
    gear: typing.List[Item] = attr.ib(default=None, repr=False)
    mainspec: Specialization = attr.ib(default=None, repr=False)
    offspec: Specialization = attr.ib(default=None, repr=False)

    offnote: str = attr.ib(default=None, repr=False)
    pnote: str = attr.ib(default=None, repr=False)
    guild: Guild = attr.ib(default=None)
    rank: GuildRank = attr.ib(default=None, repr=False)

    lastupdate: datetime = attr.ib(default=attr.Factory(datetime.now))

    def populate_data(self):
        p = {"realm": self.realm.realm, "guid": self.guid}
        self.data = {k:v for k,v in get("/Characters/GetCharacterData.php", params=p).json().items() if not k.isdigit()}
        self.armory = get("/Characters/GetCharacterArmoryInfo.php", params=p).json()
        self.account = Account(self.data["account"])
        self.gm = self.armory["IsGM"]
        self.name = self.data["name"]
        self.level = self.data["level"]
#        self.money = self.armory["Money"]
        self.race = Race(self.data["race"])
        self.gender = Gender(self.data["gender"])
        self.class_ = Class(self.data["class"])
        self.achievement_points = int(self.armory["AchievementPoints"])

        if not self.guild or (self.guild.guid != self.armory["GuildInfo"]["GuildId"]):
            self.guild = Guild(realm=self.realm, guid=self.armory["GuildInfo"]["GuildId"])

        self.professions = [Profession(p["Name"], p["Value"]) for p in self.armory["PrimaryProfessions"]]
        self.professions += [Profession(p["Name"], p["Value"]) for p in self.armory["SecundaryProfessions"]]
        self.gear = [Item(i["ItemEntry"], i["ItemName"], i["Slot"]) for i in self.armory["GearData"]]
        self.mainspec = Specialization.from_armory(self.armory["CharacterSpecs"]["MainSpec"], True)
        self.offspec = Specialization.from_armory(self.armory["CharacterSpecs"]["OffSpec"], False)
        self.lastupdate = datetime.now()
        return True

    @staticmethod
    def from_search_result(result):
        return Character(
            guid = result["Id"],
            realm = Realm(result["Realm"]),
            name = result["Name"],
            level = result["Level"],
            class_ = Class(result["Class"]),
            race = Race(result["Race"]),
            gender = Gender(result["Gender"])
        )

@attr.s
class ArenaTeam(PrecisionRealmObject):
    type_: int = attr.ib()
    name: str = attr.ib()
    def __repr__(self):
        return "ArenaTeam(type={0}x{0}, name={1}".format(self.type_, self.name)
    @staticmethod
    def from_search_result(result):
        return ArenaTeam(
            guid = result["Id"],
            realm = Realm(result["Realm"]),
            name = result["Name"],
            type_ = result["Type"]
        )
