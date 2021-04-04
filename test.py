import unittest

from precisionapi import Guild, Realm

class TestModels(unittest.TestCase):
    def test_guild_get_members(self):
        g = Guild(guid=6, realm=Realm(1))
        members = g.get_members(limit=1)
        self.assertIsNot(len(members), 0)

if __name__ == "__main__":
    unittest.main()
