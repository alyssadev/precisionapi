import attr

@attr.s
class Profession:
    profession: str = attr.ib()
    value: int = attr.ib()
    def __repr__(self):
        return f"{self.profession} ({self.value})"
