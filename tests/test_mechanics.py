import unittest
from core.unit import Knight, Pikeman, Crossbowman
from core.map import Map

class TestCombatMechanics(unittest.TestCase):
    def setUp(self):
        # Create a dummy map (flat)
        self.game_map = Map(10, 10)

    def test_pikeman_bonus_vs_cavalry(self):
        """Test that Pikeman deals bonus damage to Cavalry (Knight)."""
        pikeman = Pikeman(1, 0, (0,0))
        knight = Knight(2, 1, (1,0))

        # Expected damage:
        # Pikeman Attack: 4
        # Bonus vs Cavalry: 22
        # Total Attack: 26
        # Knight Armor (Melee): 2
        # Final Damage: 24

        damage = pikeman.calculate_damage(knight, self.game_map)
        self.assertEqual(damage, 24, "Pikeman should deal 24 damage to Knight (4 + 22 - 2)")

    def test_knight_vs_pikeman(self):
        """Test Knight vs Pikeman (no bonus)."""
        knight = Knight(1, 0, (0,0))
        pikeman = Pikeman(2, 1, (1,0))

        # Expected damage:
        # Knight Attack: 10
        # Pikeman Armor (Melee): 0
        # Final Damage: 10

        damage = knight.calculate_damage(pikeman, self.game_map)
        self.assertEqual(damage, 10, "Knight should deal 10 damage to Pikeman")

    def test_elevation_bonus(self):
        """Test that high ground gives +25% damage."""
        archer1 = Crossbowman(1, 0, (0,0)) # Will be at elevation 4
        archer2 = Crossbowman(2, 1, (2,0)) # Will be at elevation 0

        # Set elevation
        self.game_map.get_tile(0, 0).elevation = 4
        self.game_map.get_tile(2, 0).elevation = 0

        # Archer vs Archer
        # Attack: 5
        # Bonus vs Standard Building: 1 (irrelevant)
        # Armor (Pierce): 0
        # Base Damage: 5
        # Elevation Bonus: x1.25 -> 6.25 -> int(6)

        damage = archer1.calculate_damage(archer2, self.game_map)
        self.assertEqual(damage, 6, "High ground should increase damage to 6")

        # Low ground penalty: x0.75 -> 3.75 -> int(3)
        damage_low = archer2.calculate_damage(archer1, self.game_map)
        self.assertEqual(damage_low, 3, "Low ground should decrease damage to 3")

if __name__ == '__main__':
    unittest.main()
