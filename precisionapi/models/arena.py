import attr

from .enums import Realm
from .precision import PrecisionRealmObject

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
