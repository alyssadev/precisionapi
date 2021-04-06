import attr

@attr.s
class GuildRanking:
    guildid: int = attr.ib()
    name: str = attr.ib()
    progressionPoints: int = attr.ib()
    leaderguid: int = attr.ib()
    rank: int = attr.ib()
