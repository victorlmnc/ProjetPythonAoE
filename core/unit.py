# core/unit.py
import math
import logging
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
                 pos: tuple[float, float],
                 hitbox_radius: float = 0.2,
                 reload_time: float = 2.0): # NOUVEAU: Temps de rechargement (en secondes/tours logiques)

        self.unit_id: int = unit_id
        self.army_id: int = army_id
        self.statut="walk"
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

        # Gestion du Cooldown (Temps Réel)
        self.reload_time = reload_time
        self.current_cooldown = 0.0 # Prêt à tirer si <= 0

        # Tags pour recevoir des dégâts bonus (ex: Je suis une Cavalerie)
        self.armor_classes: list[str] = armor_classes
        # Dégâts bonus infligés (ex: Je fais +22 contre la Cavalerie)
        self.bonus_damage: dict[str, int] = bonus_damage

        self.pos: tuple[float, float] = pos
        self.is_alive: bool = True
        # Animation control (index + speed in ms per frame)
        self.anim_index: int = 0
        self.anim_speed: int = 150  # milliseconds per frame (lower = faster)
        self.anim_elapsed: int = 0  # accumulated milliseconds
        # Nombre de frames par état (colonnes). Valeur par défaut = 30.
        self.anim_frames_per_state: dict[str, int] = {
            'attack': 30,
            'walk': 30,
            'idle': 30,
        }
        # Champ d'animation: frames et temporisation (pas d'animation "play once" spécifique)
        self.anim_play_once_remaining: int = 0
        self.orientation: float = 0.0 # Orientation en degrés (Cartésien)

        # Last position (used to estimate facing/orientation)
        self.last_pos: tuple[float, float] = pos

    def tick_animation(self, delta_ms: int):
        """Avance l'animation interne de l'unité de delta_ms millisecondes."""
        try:
            ms = int(delta_ms)
        except Exception:
            return
        if not hasattr(self, 'anim_speed') or self.anim_speed <= 0:
            return
        self.anim_elapsed += ms

        if self.anim_elapsed >= self.anim_speed:
            advance = int(self.anim_elapsed // self.anim_speed)
            self.anim_elapsed = self.anim_elapsed % self.anim_speed

            # Gestion de l'animation "Play Once" (ex: attaque)
            if self.anim_play_once_remaining > 0:
                self.anim_play_once_remaining = max(0, self.anim_play_once_remaining - advance)

            self.anim_index = self.anim_index + advance

            # Gestion du bouclage selon le statut
            statut = getattr(self, 'statut', 'idle')
            frames = self.anim_frames_per_state.get(statut, 30)

            if frames > 0:
                if statut == 'death':
                    # Ne pas boucler l'animation de mort, s'arrêter à la dernière frame
                    self.anim_index = min(self.anim_index, frames - 1)
                else:
                    # Bouclage normal
                    self.anim_index = self.anim_index % frames

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

    def _center_squared_distance(self, target_unit: 'Unit') -> float:
        """Returns squared distance between unit centers (avoid sqrt for comparisons)."""
        dx = self.pos[0] - target_unit.pos[0]
        dy = self.pos[1] - target_unit.pos[1]
        return dx * dx + dy * dy

    def can_attack(self, target_unit: 'Unit') -> bool:
        if not self.is_alive or not target_unit.is_alive:
            return False
        # Use squared distance check to avoid calling sqrt frequently
        center_dist_sq = self._center_squared_distance(target_unit)
        # include hitbox radii + small tolerance
        range_with_hitboxes = self.attack_range + 0.1 + self.hitbox_radius + target_unit.hitbox_radius
        return center_dist_sq <= (range_with_hitboxes * range_with_hitboxes)
    def status(self, target_unit=None):
        if not self.is_alive:
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
            logger = logging.getLogger(__name__)
            logger.debug("COMBAT: %s attaque %s", self, target_unit)
            target_unit.take_damage(final_damage)
            
            # Reset du cooldown
            self.current_cooldown = self.reload_time
        else:
            pass

    def take_damage(self, amount: int):
        self.current_hp -= amount
        # log damage for debug
        logger = logging.getLogger(__name__)
        logger.debug("subit %d dégâts (HP restants: %d)", amount, self.current_hp)
        if self.current_hp <= 0:
            self.current_hp = 0
            # Marquer l'unité comme morte et demander suppression immédiate
            self.is_alive = False
            # clear cible
            if hasattr(self, 'target_id'):
                try:
                    del self.target_id
                except Exception:
                    pass
            logger.info("%s EST MORT!", self)


# --- Unités Spécifiques (Stats AoE2 Âge des Châteaux) ---

class Knight(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=100, speed=1.35, attack_power=10, attack_range=0.5, # Melee range courte
            attack_type=DMG_MELEE, melee_armor=2, pierce_armor=2, line_of_sight=4,
            armor_classes=["Cavalry", UC_UNIQUE_UNIT],
            bonus_damage={},
            hitbox_radius=0.3,
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
            hitbox_radius=0.2,
            reload_time=3.0 # Lent (cf PDF)
        )

class Crossbowman(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=35, speed=0.96, attack_power=5, attack_range=5.0,
            attack_type=DMG_PIERCE, melee_armor=0, pierce_armor=0, line_of_sight=7,
            armor_classes=["Archer"], # Fixed case
            bonus_damage={
                "Base Melee": 4,
                UC_STANDARD_BUILDING: 1,
                "Archer": 0, # Fixed key
            },
            hitbox_radius=0.2,
            reload_time=2.0 # Moyen
        )

class LongSwordsman(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=60, speed=0.9, attack_power=9, attack_range=0.5,
            attack_type=DMG_MELEE, melee_armor=1, pierce_armor=1, line_of_sight=4,
            armor_classes=["Infantry"], # Fixed case
            bonus_damage={UC_STANDARD_BUILDING: 2},
            hitbox_radius=0.2,
            reload_time=2.0
        )

class EliteSkirmisher(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=35, speed=0.96, attack_power=3, attack_range=5.0,
            attack_type=DMG_PIERCE, melee_armor=0, pierce_armor=4, line_of_sight=7,
            armor_classes=["Archer"], # Fixed case
            bonus_damage={"Archer": 3, "Spearman": 3}, # Fixed key "All Archers" -> "Archer"
            hitbox_radius=0.2,
            reload_time=3.0 # Lent
        )

class CavalryArcher(Unit):
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=50, speed=1.4, attack_power=6, attack_range=4.0,
            attack_type=DMG_PIERCE, melee_armor=1, pierce_armor=0, line_of_sight=6,
            armor_classes=["Archer", "Cavalry"], # Fixed case
            bonus_damage={"Spearman": 2},
            hitbox_radius=0.3,
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
            hitbox_radius=0.4,
            reload_time=6.0 # Très lent
        )
        # L'Onager fait des dégâts de zone (rayon de splash)
        self.splash_radius = 1.5

class LightCavalry(Unit):
    """Cavalerie légère - Rapide mais fragile, bon pour le harcèlement."""
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=60, speed=1.5, attack_power=7, attack_range=0.5,
            attack_type=DMG_MELEE, melee_armor=0, pierce_armor=2, line_of_sight=6,
            armor_classes=["Cavalry"],
            bonus_damage={"Monk": 10},  # Bonus contre les moines
            hitbox_radius=0.3,
            reload_time=2.0
        )

class Scorpion(Unit):
    """Machine de siège à projectiles perforants - Dégâts en ligne."""
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=40, speed=0.65, attack_power=12, attack_range=7.0,
            attack_type=DMG_PIERCE, melee_armor=0, pierce_armor=5, line_of_sight=9,
            armor_classes=["siege"],
            bonus_damage={"Elephant": 6, "Infantry": 0},  # Les projectiles traversent
            hitbox_radius=0.4,
            reload_time=3.6
        )
        # Le Scorpion fait des dégâts en ligne (bolt traverse les unités)
        self.pierce_targets = 3  # Nombre max de cibles traversées

class CappedRam(Unit):
    """Bélier amélioré - Très résistant aux projectiles, anti-bâtiment."""
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=200, speed=0.5, attack_power=4, attack_range=0.5,
            attack_type=DMG_MELEE, melee_armor=-3, pierce_armor=195, line_of_sight=3,
            armor_classes=["siege", "Ram"],
            bonus_damage={UC_STANDARD_BUILDING: 200, UC_STONE_DEFENSE: 65},
            hitbox_radius=0.5,
            reload_time=5.0
        )

class Trebuchet(Unit):
    """
    Machine de siège à très longue portée - Doit se déployer pour attaquer.
    Stats en mode déployé (packed = mobilité, unpacked = attaque).
    """
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=150, speed=0.0, attack_power=200, attack_range=16.0,  # Mode déployé
            attack_type=DMG_MELEE, melee_armor=1, pierce_armor=150, line_of_sight=19,
            armor_classes=["siege"],
            bonus_damage={UC_STANDARD_BUILDING: 250, UC_STONE_DEFENSE: 250},
            hitbox_radius=0.6,
            reload_time=10.0  # Très lent
        )
        self.is_deployed = True  # True = peut tirer, False = peut bouger
        self.packed_speed = 0.8  # Vitesse quand plié
        self.splash_radius = 0.5

class EliteWarElephant(Unit):
    """
    Éléphant de guerre d'élite - Énorme, lent, dégâts de zone (piétinement).
    Bonus contre les bâtiments.
    """
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=620, speed=0.6, attack_power=20, attack_range=0.5,
            attack_type=DMG_MELEE, melee_armor=1, pierce_armor=3, line_of_sight=5,
            armor_classes=["Cavalry", "Elephant", UC_UNIQUE_UNIT],
            bonus_damage={UC_STANDARD_BUILDING: 7},
            hitbox_radius=0.45,
            reload_time=2.0
        )
        # Dégâts de zone (piétinement) - Inflige des dégâts aux unités proches
        self.trample_radius = 0.8
        self.trample_damage_ratio = 0.5  # 50% des dégâts aux unités adjacentes

class Monk(Unit):
    """
    Moine - Peut soigner les unités alliées et convertir les ennemis.
    Ne fait pas de dégâts directs.
    """
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=30, speed=0.7, attack_power=0, attack_range=9.0,  # Portée de conversion
            attack_type=DMG_MELEE, melee_armor=0, pierce_armor=0, line_of_sight=11,
            armor_classes=["Monk"],
            bonus_damage={},
            hitbox_radius=0.2,
            reload_time=1.0
        )
        # Capacités spéciales du Moine
        self.heal_rate = 2  # HP soignés par tick
        self.conversion_range = 9.0
        self.conversion_time = 4.0  # Temps requis pour convertir
        self.has_relic = False  # Peut porter une relique

# --- Bâtiments ---

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
    """
    Merveille - Condition de victoire. Sa destruction = défaite immédiate.
    """
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=4800, speed=0, attack_power=0, attack_range=0,
            attack_type=DMG_MELEE, melee_armor=0, pierce_armor=0, line_of_sight=6,
            armor_classes=[UC_BUILDING, UC_STANDARD_BUILDING],
            bonus_damage={},
            hitbox_radius=5.0
        )
