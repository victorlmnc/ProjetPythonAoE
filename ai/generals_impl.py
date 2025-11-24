# ai/generals_impl.py
from ai.general import General, Action
from core.map import Map
from core.unit import Unit
import random

# (req 3)
class CaptainBRAINDEAD(General):
    """
    IA stupide: bouge aléatoirement, attaque si à portée.
    """
    def decide_actions(self, current_map: Map, my_units: list[Unit], enemy_units: list[Unit]) -> list[Action]:
        actions = []
        for unit in my_units:
            # 1. Tenter d'attaquer
            target = None
            for enemy in enemy_units:
                if unit.can_attack(enemy):
                    target = enemy
                    break # Attaque le premier trouvé
            
            if target:
                actions.append(("attack", unit.unit_id, target.unit_id))
            else:
                # 2. Bouger aléatoirement
                target_pos = (
                    unit.pos[0] + random.uniform(-unit.speed, unit.speed),
                    unit.pos[1] + random.uniform(-unit.speed, unit.speed)
                )
                actions.append(("move", unit.unit_id, target_pos))
        return actions

# (req 3)
class MajorDAFT(General):
    """
    IA simple: s'approche de l'ennemi le plus proche et attaque.
    """
    def decide_actions(self, current_map: Map, my_units: list[Unit], enemy_units: list[Unit]) -> list[Action]:
        actions = []
        if not enemy_units:
            return [] # Plus d'ennemis

        for unit in my_units:
            # Utilise l'optimisation de la 'map' !
            # "Donne-moi les ennemis dans un rayon de 1000.0"
            # C'est BEAUCOUP plus rapide que de scanner 'enemy_units'
            nearby_enemies = current_map.get_nearby_units(unit, 1000.0) 
            
            # (Pour cet exemple, on filtre pour n'avoir que les ennemis réels)
            nearby_enemies = [e for e in nearby_enemies if e.army_id != self.army_id]

            if not nearby_enemies:
                # Si personne n'est trouvé par la map, utilise la liste globale
                closest_enemy = self.find_closest_enemy(unit, enemy_units)
            else:
                closest_enemy = self.find_closest_enemy(unit, nearby_enemies)

            if not closest_enemy:
                continue # Aucun ennemi vivant

            # 1. Tenter d'attaquer
            if unit.can_attack(closest_enemy):
                actions.append(("attack", unit.unit_id, closest_enemy.unit_id))
            
            # 2. Sinon, bouger
            else:
                # Bouge vers la position de l'ennemi
                actions.append(("move", unit.unit_id, closest_enemy.pos))
                
        return actions