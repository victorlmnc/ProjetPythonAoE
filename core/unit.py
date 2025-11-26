# core/unit.py
import math
from typing import Optional

class Unit:
    """
    Classe de base pour une unité avec stats AoE2 complètes.
    Gère les résistances (Armure) et les bonus de dégâts (Contres).
    """
    def __init__(self,
                 unit_id: int,
                 army_id: int,
                 hp: int,
                 speed: float,
                 attack_power: int,
                 attack_range: float,
                 attack_type: str,     # "melee" ou "pierce"
                 melee_armor: int,
                 pierce_armor: int,
                 line_of_sight: int,
                 armor_classes: list[str], # ex: ["Infantry", "Spearman"]
                 bonus_damage: dict[str, int], # ex: {"Cavalry": 22}
                 pos: tuple[float, float],
                 hitbox_radius: float = 0.5):

        self.unit_id: int = unit_id
        self.army_id: int = army_id

        self.max_hp: int = hp
        self.current_hp: int = hp

        self.speed: float = speed
        self.attack_power: int = attack_power
        self.attack_range: float = attack_range
        self.attack_type: str = attack_type

        self.melee_armor: int = melee_armor
        self.pierce_armor: int = pierce_armor

        self.line_of_sight: int = line_of_sight

        self.hitbox_radius: float = hitbox_radius

        # Tags pour recevoir des dégâts bonus (ex: Je suis une Cavalerie)
        self.armor_classes: list[str] = armor_classes
        # Dégâts bonus infligés (ex: Je fais +22 contre la Cavalerie)
        self.bonus_damage: dict[str, int] = bonus_damage

        self.pos: tuple[float, float] = pos
        self.is_alive: bool = True

    def __repr__(self) -> str:
        pos_str = f"({self.pos[0]:.1f}, {self.pos[1]:.1f})"
        return f"{self.__class__.__name__}({self.unit_id}, HP:{self.current_hp}/{self.max_hp}, Pos:{pos_str})"

    def _calculate_distance(self, target_unit: 'Unit') -> float:
        """ Calculates the distance between the edges of two units' hitboxes. """
        dist = math.sqrt(
            (self.pos[0] - target_unit.pos[0])**2 +
            (self.pos[1] - target_unit.pos[1])**2
        )
        return max(0, dist - self.hitbox_radius - target_unit.hitbox_radius)

    def can_attack(self, target_unit: 'Unit') -> bool:
        if not self.is_alive or not target_unit.is_alive:
            return False
        distance = self._calculate_distance(target_unit)
        # On ajoute une petite tolérance (0.1) pour les erreurs de flottants
        return distance <= (self.attack_range + 0.1)

    def attack(self, target_unit: 'Unit'):
        if self.can_attack(target_unit):
            # 1. Calcul du Bonus
            total_bonus = 0
            for armor_class in target_unit.armor_classes:
                if armor_class in self.bonus_damage:
                    total_bonus += self.bonus_damage[armor_class]

            # 2. Récupération de l'armure cible
            target_armor = 0
            if self.attack_type == "melee":
                target_armor = target_unit.melee_armor
            elif self.attack_type == "pierce":
                target_armor = target_unit.pierce_armor

            # 3. Formule AoE2 : Max(1, (Attaque + Bonus) - Armure)
            raw_damage = (self.attack_power + total_bonus) - target_armor
            final_damage = max(1, raw_damage)

            print(f"COMBAT: {self} attaque {target_unit}")
            if total_bonus > 0:
                print(f"   -> BONUS CRITIQUE! (+{total_bonus} dmg)")

            target_unit.take_damage(final_damage)
        else:
            # (Optionnel) Trop verbeux pour le mode tournoi, à commenter plus tard
            # print(f"{self} hors de portée de {target_unit}")
            pass

    def take_damage(self, amount: int):
        self.current_hp -= amount
        print(f"   -> subit {amount} dégâts (HP restants: {self.current_hp})")
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
            print(f"   -> {self} EST MORT!")


# --- Unités Spécifiques (Stats AoE2 Âge des Châteaux) ---

class Knight(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=100, speed=1.35, attack_power=10, attack_range=1.5,
            attack_type="melee", melee_armor=2, pierce_armor=2, line_of_sight=4,
            armor_classes=["Cavalry", "Unique"],
            bonus_damage={},
            hitbox_radius=0.7
        )

class Pikeman(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=55, speed=1.0, attack_power=4, attack_range=1.5,
            attack_type="melee", melee_armor=0, pierce_armor=0, line_of_sight=4,
            armor_classes=["Infantry", "Spearman"],
            bonus_damage={"Cavalry": 22, "Elephant": 25},
            hitbox_radius=0.4
        )

class Crossbowman(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=35, speed=0.96, attack_power=5, attack_range=5.0,
            attack_type="pierce", melee_armor=0, pierce_armor=0, line_of_sight=7,
            armor_classes=["archer"],
            bonus_damage={
                "Base Melee": 4,
                "Standard Buildings": 1,
                "All Archers": 0,
            },
            hitbox_radius=0.4
        )

class LongSwordsman(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=60, speed=0.9, attack_power=9, attack_range=1.5,
            attack_type="melee", melee_armor=1, pierce_armor=1, line_of_sight=4,
            armor_classes=["infantry"],
            bonus_damage={"Standard Buildings": 2},
            hitbox_radius=0.4
        )

class EliteSkirmisher(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=35, speed=0.96, attack_power=3, attack_range=5.0,
            attack_type="pierce", melee_armor=0, pierce_armor=4, line_of_sight=7,
            armor_classes=["archer"],
            bonus_damage={"All Archers": 3, "Spearman": 3},
            hitbox_radius=0.4
        )

class CavalryArcher(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=50, speed=1.4, attack_power=6, attack_range=4.0,
            attack_type="pierce", melee_armor=1, pierce_armor=0, line_of_sight=6,
            armor_classes=["archer", "cavalry"],
            bonus_damage={"Spearman": 2},
            hitbox_radius=0.7
        )

class Onager(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=50, speed=0.6, attack_power=50, attack_range=8.0,
            attack_type="melee", melee_armor=0, pierce_armor=2, line_of_sight=10,
            armor_classes=["siege"],
            bonus_damage={"Standard Buildings": 10},
            hitbox_radius=1.0
        )

class Castle(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=4800, speed=0, attack_power=11, attack_range=8.0,
            attack_type="pierce", melee_armor=8, pierce_armor=8, line_of_sight=10,
            armor_classes=["building"],
            bonus_damage={},
            hitbox_radius=2.5
        )

class Wonder(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=4800, speed=0, attack_power=0, attack_range=0,
            attack_type="melee", melee_armor=0, pierce_armor=0, line_of_sight=6,
            armor_classes=["building"],
            bonus_damage={},
            hitbox_radius=5.0
        )