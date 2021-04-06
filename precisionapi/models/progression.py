import attr
import typing

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
