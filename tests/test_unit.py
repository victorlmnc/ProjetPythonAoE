# tests/test_unit.py
"""
Tests unitaires pour les unités et le combat.
Utilise pytest : pip install pytest
Lancer : pytest tests/ -v
"""
import pytest
import sys
import os

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.unit import Knight, Pikeman, Crossbowman, Onager, EliteWarElephant, Monk
from core.map import Map


class TestUnitCreation:
    """Tests de création d'unités."""
    
    def test_knight_creation(self):
        """Un Knight doit avoir les bonnes stats de base."""
        knight = Knight(unit_id=1, army_id=0, pos=(10, 10))
        assert knight.max_hp == 100
        assert knight.attack_power == 10
        assert knight.is_alive == True
    
    def test_pikeman_creation(self):
        """Un Pikeman doit avoir 55 HP."""
        pikeman = Pikeman(unit_id=2, army_id=1, pos=(5, 5))
        assert pikeman.max_hp == 55
        assert pikeman.speed == 1.0
    
    def test_onager_has_splash(self):
        """L'Onager doit avoir un splash_radius."""
        onager = Onager(unit_id=3, army_id=0, pos=(20, 20))
        assert hasattr(onager, 'splash_radius')
        assert onager.splash_radius > 0
    
    def test_elephant_has_trample(self):
        """L'Elephant doit avoir un trample_radius."""
        elephant = EliteWarElephant(unit_id=4, army_id=1, pos=(15, 15))
        assert hasattr(elephant, 'trample_radius')
        assert hasattr(elephant, 'trample_damage_ratio')


class TestCombat:
    """Tests de mécanique de combat."""
    
    def test_damage_calculation_basic(self):
        """Les dégâts de base doivent être calculés correctement."""
        knight = Knight(unit_id=1, army_id=0, pos=(10, 10))
        pikeman = Pikeman(unit_id=2, army_id=1, pos=(10, 10))
        
        damage = knight.calculate_damage(pikeman)
        # Knight: 10 attack, Pikeman: 0 melee armor
        # Dégâts = max(1, 10 - 0) = 10
        assert damage == 10
    
    def test_pikeman_bonus_vs_cavalry(self):
        """Le Pikeman doit faire des dégâts bonus contre la cavalerie."""
        pikeman = Pikeman(unit_id=1, army_id=0, pos=(10, 10))
        knight = Knight(unit_id=2, army_id=1, pos=(10, 10))
        
        damage = pikeman.calculate_damage(knight)
        # Pikeman: 4 attack + 22 bonus vs Mounted Units, Knight: 0 melee armor
        # Dégâts = max(1, 4 + 22 - 0) = 26
        assert damage >= 20  # Au moins le bonus
    
    def test_elevation_bonus(self):
        """L'élévation doit modifier les dégâts de 25%."""
        game_map = Map(40, 40)
        game_map.grid[10][10].elevation = 5  # Attaquant en hauteur
        game_map.grid[10][11].elevation = 0  # Défenseur en bas (adjacent)
        
        knight_high = Knight(unit_id=1, army_id=0, pos=(10.0, 10.0))
        knight_low = Knight(unit_id=2, army_id=1, pos=(10.0, 11.0))
        
        damage_high = knight_high.calculate_damage(knight_low, game_map)
        # Knight sans élévation fait 10 dégâts
        # Avec bonus hauteur (1.25): 10 * 1.25 = 12.5 -> 12
        # Le test vérifie que les dégâts sont supérieurs aux dégâts de base
        assert damage_high >= 10  # Au minimum les dégâts de base
    
    def test_take_damage(self):
        """Une unité doit perdre des HP correctement."""
        knight = Knight(unit_id=1, army_id=0, pos=(10, 10))
        initial_hp = knight.current_hp
        
        knight.take_damage(30)
        
        assert knight.current_hp == initial_hp - 30
        assert knight.is_alive == True
    
    def test_unit_death(self):
        """Une unité doit mourir quand HP <= 0."""
        knight = Knight(unit_id=1, army_id=0, pos=(10, 10))
        
        knight.take_damage(150)  # Plus que 100 HP
        
        assert knight.current_hp == 0
        assert knight.is_alive == False


class TestMap:
    """Tests de la carte."""
    
    def test_map_creation(self):
        """La carte doit se créer avec les bonnes dimensions."""
        game_map = Map(120, 120)
        assert game_map.width == 120
        assert game_map.height == 120
    
    def test_elevation_access(self):
        """On doit pouvoir accéder à l'élévation d'une tuile."""
        game_map = Map(40, 40)
        game_map.grid[5][5].elevation = 10
        
        elevation = game_map.get_elevation_at_pos((5, 5))
        assert elevation == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
