import unittest

from precisionapi import Guild, Realm, Character

class TestModels(unittest.TestCase):
    def test_character_populate(self):
        c = Character(guid=9832, realm=Realm(1))
        c.populate_data()
        self.assertIs(type(c.data), dict)

    def test_guild_get_members(self):
        g = Guild(guid=6, realm=Realm(1))
        members = g.get_members(limit=1)
        self.assertIsNot(len(members), 0)

if __name__ == "__main__":
    unittest.main()
