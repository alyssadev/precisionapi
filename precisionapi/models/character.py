import attr
import typing
from datetime import datetime

from ..util import get
from .precision import PrecisionRealmObject, Account
from .enums import Race, Gender, Class, Realm
from .item import Item
from .profession import Profession
from .specialization import Specialization
from .guild import Guild, GuildRank
from .progression import Progression

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