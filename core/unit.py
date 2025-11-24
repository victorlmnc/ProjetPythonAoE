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
                 armor_classes: list[str], # ex: ["Infantry", "Spearman"]
                 bonus_damage: dict[str, int], # ex: {"Cavalry": 22}
                 pos: tuple[float, float]):
        
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
        return math.sqrt(
            (self.pos[0] - target_unit.pos[0])**2 +
            (self.pos[1] - target_unit.pos[1])**2
        )

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
    """
    Chevalier:
    Fort en mêlée, grosse armure, mais vulnérable aux Piquiers.
    """
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=100, 
            speed=1.35,          # Rapide
            attack_power=10, 
            attack_range=1.5,    # Corps à corps
            attack_type="melee",
            melee_armor=2,       # Solide
            pierce_armor=2,      # Résiste aux flèches
            armor_classes=["Cavalry", "Unique"],
            bonus_damage={}      # Pas de bonus spécial
        )

class Pikeman(Unit):
    """
    Piquier:
    Faible stats de base, mais TUEUR DE CHEVALIERS (+22 dmg).
    """
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=55, 
            speed=1.0,           # Moyen
            attack_power=4,      # Très faible attaque de base...
            attack_range=1.5, 
            attack_type="melee",
            melee_armor=0,       # Pas d'armure
            pierce_armor=0,      # Très vulnérable aux flèches
            armor_classes=["Infantry", "Spearman"],
            # LE POINT CLÉ: +22 dégâts contre la Cavalerie
            bonus_damage={"Cavalry": 22, "Elephant": 25} 
        )

class Crossbowman(Unit):
    """
    Arbalétrier: Attaque à distance avec une grande précision.
    """
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, army_id=army_id, pos=pos,
            hp=35, speed=0.96, attack_power=5, attack_range=5.0,
            attack_type="pierce", 
            melee_armor=0, pierce_armor=0,
            armor_classes=["archer"],
            bonus_damage={
                "Base Melee": 4,       # Bonus contre les unités de mêlée de base
                "Standard Buildings": 1,    # Bonus contre les bâtiments standard
                "All Archers": 0,      # Pas de bonus contre les archers
            }
        )