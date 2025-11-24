# core/unit.py
import math
from typing import Optional

class Unit:
    """
    Classe de base pour une unité avec position flottante.
    Elle gère ses propres statistiques et sa logique de combat.
    """
    def __init__(self, 
                 unit_id: int, 
                 army_id: int, 
                 hp: int, 
                 speed: float, 
                 attack_power: int, 
                 attack_range: float, 
                 cost: int, 
                 pos: tuple[float, float]):
        
        self.unit_id: int = unit_id  # Identifiant unique
        self.army_id: int = army_id  # 0 ou 1
        
        self.max_hp: int = hp
        self.current_hp: int = hp
        
        self.speed: float = speed          # Cases/unités par tour (flottant)
        self.attack_power: int = attack_power
        self.attack_range: float = attack_range  # 1.5 pour mêlée, 7.0 pour archer
        
        self.pos: tuple[float, float] = pos # (x, y) en flottants
        self.is_alive: bool = True

    def __repr__(self) -> str:
        """
        Représentation textuelle pour le débogage.
        Utilise les f-strings (sec 22.4.10.4) pour formater les flottants.
        """
        pos_str = f"({self.pos[0]:.1f}, {self.pos[1]:.1f})"
        return f"{self.__class__.__name__}({self.unit_id}, HP: {self.current_hp}, Pos: {pos_str})"

    def _calculate_distance(self, target_unit: 'Unit') -> float:
        """Calcule la distance Euclidienne (pythagore)."""
        return math.sqrt(
            (self.pos[0] - target_unit.pos[0])**2 +
            (self.pos[1] - target_unit.pos[1])**2
        )

    def can_attack(self, target_unit: 'Unit') -> bool:
        """Vérifie si la cible est à portée (en flottant)."""
        if not self.is_alive or not target_unit.is_alive:
            return False
            
        distance = self._calculate_distance(target_unit)
        return distance <= self.attack_range

    def attack(self, target_unit: 'Unit'):
        """L'unité attaque une unité cible."""
        if self.can_attack(target_unit):
            print(f"{self} ATTAQUE {target_unit}!")
            target_unit.take_damage(self.attack_power)
        else:
            print(f"{self} essaie d'attaquer {target_unit} mais est hors de portée.")

    def take_damage(self, amount: int):
        """Réduit les PV de l'unité et la marque comme morte si nécessaire."""
        self.current_hp -= amount
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
            print(f"{self} est MORT!")


# --- Implémentation des Unités Spécifiques (Héritage, sec 27.8) ---

class Knight(Unit):
    """
    Le Chevalier: Fort, rapide, coûteux.
    """
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=100, speed=2.0, attack_power=10, attack_range=1.5
        )

class Pikeman(Unit):
    """
    Le Piquier: Faible, lent, efficace contre les chevaliers.
    """
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=60, speed=1.0, attack_power=5, attack_range=1.5
        )

class Archer(Unit):
    """
    L'Archer: Attaque à distance, faible en mêlée.
    """
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=40, speed=1.0, attack_power=4, attack_range=7.0
        )