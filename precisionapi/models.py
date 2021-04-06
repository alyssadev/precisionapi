import attr
import requests
from datetime import datetime, timedelta
import typing
from enum import IntEnum

from .variables import API_URL
from .util import retrieve_all_results, get

class Enum(IntEnum):
    def __repr__(self):
        return self.name

class Realm(Enum):
    PTR = 0
    Precision = 1

class Race(Enum):
    Human    = 1
    Orc      = 2
    Dwarf    = 3
    NightElf = 4
    Undead   = 5
    Tauren   = 6
    Gnome    = 7
    Troll    = 8
    Goblin   = 9
    BloodElf = 10
    Draenei  = 11
    Worgen   = 22

class Class(Enum):
    Warrior     = 1
    Paladin     = 2
    Hunter      = 3
    Rogue       = 4
    Priest      = 5
    DeathKnight = 6
    Shaman      = 7
    Mage        = 8
    Warlock     = 9
    Druid       = 11

class Gender(Enum):
    Male = 0
    Female = 1

@attr.s
class DungeonEncounter:
    EncounterId: int = attr.ib()
    DungeonId: int = attr.ib()
    CreatureEntry: int = attr.ib()
    Description: str = attr.ib()
    Points: int = attr.ib()
    CompletedCount: int = attr.ib()
    IsComplete: bool = attr.ib()

@attr.s
class DungeonProgressionClass:
    DungeonId: int = attr.ib()
    Name: str = attr.ib()
    MinPatch: int = attr.ib()
    MapId: int = attr.ib()
    QuestRequirement: int = attr.ib()
    KeyRequirement: int = attr.ib()
    RetailDungeonId: int = attr.ib()
    AchievementRequirement: int = attr.ib()
    EncounterData: typing.List[DungeonEncounter] = attr.ib()


@attr.s
class RaidEncounter:
    EncounterId: int = attr.ib()
    RaidId: int = attr.ib()
    Description: str = attr.ib()
    Type: int = attr.ib()
    RequiredCreatureId: int = attr.ib()
    Notes: str = attr.ib()
    IsLastBoss: int = attr.ib()
    RealmFirstReward: int = attr.ib()
    RealmFirstRewardCount: int = attr.ib()
    Points: int = attr.ib()
    CompletedCount: int = attr.ib()
    IsComplete: bool = attr.ib()

@attr.s
class RaidProgressionClass:
    RaidId: int = attr.ib()
    RaidName: str = attr.ib()
    MinPatch: int = attr.ib()
    MapId: int = attr.ib()
    QuestRequirement: int = attr.ib()
    QuestRequirement2: int = attr.ib()
    AchievementRequirement: int = attr.ib()
    FirstExpansionRaid: int = attr.ib()
    ItemRequirement1: int = attr.ib()
    ItemRequirement2: int = attr.ib()
    EncounterData: typing.List[RaidEncounter] = attr.ib()

@attr.s
class Progression:
    PercentCompleted: float = attr.ib()
    RaidCompletedCount: int = attr.ib()
    RaidTotalAvailable: int = attr.ib()
    DungeonCompletedCount: int = attr.ib()
    DungeonTotalAvailable: int = attr.ib()
    RaidProgression: typing.List[RaidProgressionClass] = attr.ib(repr=False)
    DungeonProgression: typing.List[DungeonProgressionClass] = attr.ib(repr=False)
    @staticmethod
    def from_progression(data):
        raids = []
        dungeons = []
        for raid in data["RaidProgression"]:
            encounters = [RaidEncounter(**{k:v for k,v in e.items() if not k.isdigit()}) for e in raid["EncounterData"]]
            raid_obj = RaidProgressionClass(EncounterData = encounters, **{k:v for k,v in raid.items() if not k.isdigit() and k != "EncounterData"})
            raids.append(raid_obj)
        for dungeon in data["DungeonProgression"]:
            encounters = [DungeonEncounter(**{k:v for k,v in e.items() if not k.isdigit()}) for e in dungeon["EncounterData"]]
            dungeon_obj = DungeonProgressionClass(EncounterData = encounters, **{k:v for k,v in dungeon.items() if not k.isdigit() and k != "EncounterData"})
            dungeons.append(dungeon_obj)
        return Progression(
            RaidProgression=raids,
            DungeonProgression=dungeons,
            **{k:v for k,v in data.items() if k not in ["RaidProgression", "DungeonProgression"]}
        )

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
            self.members_raw = retrieve_all_results("/Characters/GetGuildMembers.php", {"guildid": self.guid, "realm": self.realm.value}, limit=limit)
            self.lastupdate = datetime.now()
            self.members = [
                Character(
                    guid = m["0"],
                    realm = Realm(int(m["realm"])),
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

    def populate_data(self):
        _ = self.get_members(update=True)
        return True

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

    def populate_data(self, include_progression=False):
        p = {"realm": self.realm.value, "guid": self.guid}
        self.data = {k:v for k,v in get("/Characters/GetCharacterData.php", params=p).json().items() if not k.isdigit()}
        self.armory = get("/Characters/GetCharacterArmoryInfo.php", params=p).json()
        if include_progression:
            # the response from GetCharacterProgression is json encoded in a string, twice. for some reason
            from json import loads
            self.progression = Progression.from_progression(loads(get("/Characters/GetCharacterProgression.php", params=p).json()))
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
    type: int = attr.ib()
    name: str = attr.ib()

    def __repr__(self):
        return "ArenaTeam(type={0}x{0}, name={1}".format(self.type, self.name)

    @staticmethod
    def from_search_result(result):
        return ArenaTeam(
            guid = result["Id"],
            realm = Realm(result["Realm"]),
            name = result["Name"],
            type = result["Type"]
        )
