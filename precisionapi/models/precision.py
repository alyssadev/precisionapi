import attr

from .enums import Realm

@attr.s
class PrecisionObject:
    guid: int = attr.ib()

@attr.s
class PrecisionRealmObject(PrecisionObject):
    realm: Realm = attr.ib()

@attr.s
class Account(PrecisionObject):
    name: str = attr.ib(default=None)
