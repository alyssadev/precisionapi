import attr

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
