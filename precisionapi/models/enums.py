from enum import IntEnum

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
