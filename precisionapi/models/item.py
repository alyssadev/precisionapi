import attr

@attr.s
class Item:
    guid: int = attr.ib()
    name: str = attr.ib()
    slot: int = attr.ib(default=None)
