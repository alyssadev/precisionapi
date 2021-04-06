import attr
from datetime import datetime, timedelta

from ..util import retrieve_all_results, get
from .precision import PrecisionRealmObject
from .enums import Realm, Race, Gender, Class
from .ranking import GuildRanking

@attr.s
class Guild(PrecisionRealmObject):
    lastupdate: datetime = None
    members: list = attr.ib(default=attr.Factory(list), repr=lambda l: str(len(l)))
    name: str = attr.ib(default=None)

    def get_members(self, update=False, limit=None):
        from .character import Character
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
        rankings = get("/Characters/GetGuildProgressionRanking.php", params={"guid": self.guid, "realm": self.realm.value}).json()
        g = [_ for _ in rankings if _["guildid"] == self.guid]
        if len(g) >= 1:
            self.ranking = GuildRanking(**{k:v for k,v in g[0].items() if not k.isdigit()})
            self.name = self.ranking.name
        _ = self.get_members()
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
