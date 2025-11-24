# ai/generals_impl.py
from ai.general import General, Action
from core.map import Map
from core.unit import Unit, Archer
import random
import math

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

class ColonelKAISER(General):
    """
    IA Stratégique (Req 3).
    Concepts:
    1. Persistance : Garde la même cible pour maximiser le "Focus Fire".
    2. Kiting : Les archers fuient si un ennemi est trop proche.
    3. Opportunisme : Utilise la Map pour trouver des cibles locales.
    """
    def __init__(self, army_id: int):
        super().__init__(army_id)
        # Mémoire : dict[my_unit_id, enemy_unit_id]
        self.target_memory: dict[int, int] = {}

    def decide_actions(self, current_map: Map, my_units: list[Unit], enemy_units: list[Unit]) -> list[Action]:
        actions: list[Action] = []
        
        # Création d'un lookup rapide pour les ennemis (ID -> Unit)
        # Optimisation sec 24.4 (dict lookup est O(1))
        enemy_lookup = {u.unit_id: u for u in enemy_units}
        
        for unit in my_units:
            
            # --- STRATÉGIE 1 : KITING (Pour les Archers) ---
            if isinstance(unit, Archer):
                # Cherche l'ennemi le plus proche (très proche)
                threat = self.find_closest_enemy(unit, enemy_units)
                if threat:
                    dist = unit._calculate_distance(threat)
                    # Si l'ennemi est à moins de 30% de ma portée max, je fuis !
                    safety_distance = unit.attack_range * 0.3
                    
                    if dist < safety_distance:
                        # Calcule vecteur de fuite (opposé à l'ennemi)
                        flee_pos = self._calculate_flee_position(unit, threat)
                        actions.append(("move", unit.unit_id, flee_pos))
                        continue # L'archer a bougé, il ne peut pas attaquer ce tour-ci (simplification)

            # --- STRATÉGIE 2 : GESTION DE CIBLE (Persistance) ---
            target: Unit | None = None
            
            # A. Vérifier si j'ai déjà une cible en mémoire
            if unit.unit_id in self.target_memory:
                target_id = self.target_memory[unit.unit_id]
                candidate = enemy_lookup.get(target_id)
                
                # Si la cible existe encore, est vivante et pas trop loin (ex: 2x portée), je la garde
                if candidate and candidate.is_alive:
                     target = candidate
                else:
                    # Cible morte ou disparue, on oublie
                    del self.target_memory[unit.unit_id]

            # B. Si pas de cible, en trouver une nouvelle
            if not target:
                # Utilise la matrice creuse pour trouver les voisins (Optimisation)
                # On cherche large (20.0 unités)
                nearby = current_map.get_nearby_units(unit, 20.0)
                nearby_enemies = [u for u in nearby if u.army_id != self.army_id]
                
                if nearby_enemies:
                    target = self.find_closest_enemy(unit, nearby_enemies)
                else:
                    # Personne à côté, on cherche sur toute la carte
                    target = self.find_closest_enemy(unit, enemy_units)
                
                # Mémoriser la nouvelle cible
                if target:
                    self.target_memory[unit.unit_id] = target.unit_id

            # --- ACTION ---
            if target:
                if unit.can_attack(target):
                    actions.append(("attack", unit.unit_id, target.unit_id))
                else:
                    actions.append(("move", unit.unit_id, target.pos))
        
        return actions
    
    def _calculate_flee_position(self, unit: Unit, threat: Unit) -> tuple[float, float]:
        """Calcule une position opposée à la menace."""
        dx = unit.pos[0] - threat.pos[0]
        dy = unit.pos[1] - threat.pos[1]
        
        # Normalisation
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0: dist = 0.01
        
        # Fuir de 'speed' unités dans la direction opposée
        nx = unit.pos[0] + (dx / dist) * unit.speed
        ny = unit.pos[1] + (dy / dist) * unit.speed
        return (nx, ny)