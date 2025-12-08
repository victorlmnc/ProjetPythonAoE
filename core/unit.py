# core/unit.py
import math
from typing import Optional

# Constantes pour les types d'unités (pour éviter les chaînes magiques)
UC_BUILDING = "building"
UC_STANDARD_BUILDING = "Standard Buildings"
UC_STONE_DEFENSE = "Stone Defense"
UC_UNIQUE_UNIT = "Unique"
DMG_MELEE = "melee"
DMG_PIERCE = "pierce"

class Unit:
    """
    Classe de base pour une unité avec stats AoE2 complètes + Gestion Cooldown (RTS).
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
                 statut="walk"
                 pos: tuple[float, float],
                 hitbox_radius: float = 0.5,
                 reload_time: float = 2.0): # NOUVEAU: Temps de rechargement (en secondes/tours logiques)

        self.unit_id: int = unit_id
        self.army_id: int = army_id

        self.max_hp: int = hp
        self.current_hp: int = hp
        self.statut =statut
        self.speed: float = speed
        self.attack_power: int = attack_power
        self.attack_range: float = attack_range
        self.attack_type: str = attack_type

        self.melee_armor: int = melee_armor
        self.pierce_armor: int = pierce_armor

        self.line_of_sight: int = line_of_sight

        self.hitbox_radius: float = hitbox_radius

        # Gestion du Cooldown (Temps Réel)
        self.reload_time = reload_time
        self.current_cooldown = 0.0 # Prêt à tirer si <= 0

        # Tags pour recevoir des dégâts bonus (ex: Je suis une Cavalerie)
        self.armor_classes: list[str] = armor_classes
        # Dégâts bonus infligés (ex: Je fais +22 contre la Cavalerie)
        self.bonus_damage: dict[str, int] = bonus_damage

        self.pos: tuple[float, float] = pos
        self.is_alive: bool = True

    def __repr__(self) -> str:
        pos_str = f"({self.pos[0]:.1f}, {self.pos[1]:.1f})"
        return f"{self.__class__.__name__}({self.unit_id}, HP:{self.current_hp}/{self.max_hp}, Pos:{pos_str})"

    def tick_cooldown(self, delta: float):
        """Fait avancer le temps de rechargement."""
        if self.current_cooldown > 0:
            self.current_cooldown -= delta
            if self.current_cooldown < 0:
                self.current_cooldown = 0

    def can_act(self) -> bool:
        """Vérifie si l'unité est prête à agir (attaque)."""
        return self.current_cooldown <= 0

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
    def status(self, target_unit=None):
        if not self.is_alive:
            self.statut = "death"
        return

        if target_unit and self.can_attack(target_unit):
            self.statut = "attack"
        else:
            self.statut = "walk"

    def calculate_damage(self, target_unit: 'Unit', game_map=None) -> int:
        """
        Calcule les dégâts finaux infligés à une autre unité, en tenant compte
        des bonus, de l'armure et de l'élévation.
        """
        # 1. Calcul des bonus de dégâts
        total_bonus = sum(self.bonus_damage.get(cls, 0) for cls in target_unit.armor_classes)

        # 2. Récupération de l'armure de la cible
        target_armor = target_unit.melee_armor if self.attack_type == DMG_MELEE else target_unit.pierce_armor

        # 3. Calcul des dégâts de base
        base_damage = max(1, (self.attack_power + total_bonus) - target_armor)

        # 4. Modificateur d'élévation
        elevation_modifier = 1.0
        if game_map:
            attacker_elevation = game_map.get_elevation_at_pos(self.pos)
            defender_elevation = game_map.get_elevation_at_pos(target_unit.pos)

            if attacker_elevation > defender_elevation:
                elevation_modifier = 1.25
            elif attacker_elevation < defender_elevation:
                elevation_modifier = 0.75

        return int(base_damage * elevation_modifier)

    def attack(self, target_unit: 'Unit', game_map=None):
        """Tente d'attaquer la cible si à portée et rechargé."""
        if self.can_attack(target_unit) and self.can_act():
            final_damage = self.calculate_damage(target_unit, game_map)

            print(f"COMBAT: {self} attaque {target_unit}")
            target_unit.take_damage(final_damage)
            
            # Reset du cooldown
            self.current_cooldown = self.reload_time
        else:
            pass

    def take_damage(self, amount: int):
        self.current_hp -= amount
        # print(f"   -> subit {amount} dégâts (HP restants: {self.current_hp})")
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
            print(f"   -> {self} EST MORT!")


# --- Unités Spécifiques (Stats AoE2 Âge des Châteaux) ---

class Knight(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=100, speed=1.35, attack_power=10, attack_range=0.5, # Melee range courte
            attack_type=DMG_MELEE, melee_armor=2, pierce_armor=2, line_of_sight=4,
            armor_classes=["Cavalry", UC_UNIQUE_UNIT],
            bonus_damage={},
            hitbox_radius=0.7,
            reload_time=1.8 # Attaque rapide
        )

class Pikeman(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=55, speed=1.0, attack_power=4, attack_range=0.5,
            attack_type=DMG_MELEE, melee_armor=0, pierce_armor=0, line_of_sight=4,
            armor_classes=["Infantry", "Spearman"],
            bonus_damage={"Cavalry": 22, "Elephant": 25},
            hitbox_radius=0.4,
            reload_time=3.0 # Lent (cf PDF)
        )

class Crossbowman(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=35, speed=0.96, attack_power=5, attack_range=5.0,
            attack_type=DMG_PIERCE, melee_armor=0, pierce_armor=0, line_of_sight=7,
            armor_classes=["archer"],
            bonus_damage={
                "Base Melee": 4,
                UC_STANDARD_BUILDING: 1,
                "All Archers": 0,
            },
            hitbox_radius=0.4,
            reload_time=2.0 # Moyen
        )

class LongSwordsman(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=60, speed=0.9, attack_power=9, attack_range=0.5,
            attack_type=DMG_MELEE, melee_armor=1, pierce_armor=1, line_of_sight=4,
            armor_classes=["infantry"],
            bonus_damage={UC_STANDARD_BUILDING: 2},
            hitbox_radius=0.4,
            reload_time=2.0
        )

class EliteSkirmisher(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=35, speed=0.96, attack_power=3, attack_range=5.0,
            attack_type=DMG_PIERCE, melee_armor=0, pierce_armor=4, line_of_sight=7,
            armor_classes=["archer"],
            bonus_damage={"All Archers": 3, "Spearman": 3},
            hitbox_radius=0.4,
            reload_time=3.0 # Lent
        )

class CavalryArcher(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=50, speed=1.4, attack_power=6, attack_range=4.0,
            attack_type=DMG_PIERCE, melee_armor=1, pierce_armor=0, line_of_sight=6,
            armor_classes=["archer", "cavalry"],
            bonus_damage={"Spearman": 2},
            hitbox_radius=0.7,
            reload_time=2.0
        )

class Onager(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=50, speed=0.6, attack_power=50, attack_range=8.0,
            attack_type=DMG_MELEE, melee_armor=0, pierce_armor=2, line_of_sight=10,
            armor_classes=["siege"],
            bonus_damage={UC_STANDARD_BUILDING: 10},
            hitbox_radius=1.0,
            reload_time=6.0 # Très lent
        )

# Ces classes doivent être ici pour l'instanciation via UNIT_CLASS_MAP, 
# même si structures.py les redéfinit potentiellement mieux.
class Castle(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=4800, speed=0, attack_power=11, attack_range=8.0,
            attack_type=DMG_PIERCE, melee_armor=8, pierce_armor=8, line_of_sight=10,
            armor_classes=[UC_BUILDING, UC_STONE_DEFENSE],
            bonus_damage={},
            hitbox_radius=2.5,
            reload_time=2.0
        )

class Wonder(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=4800, speed=0, attack_power=0, attack_range=0,
            attack_type=DMG_MELEE, melee_armor=0, pierce_armor=0, line_of_sight=6,
            armor_classes=[UC_BUILDING, UC_STANDARD_BUILDING],
            bonus_damage={},
            hitbox_radius=5.0
        )
