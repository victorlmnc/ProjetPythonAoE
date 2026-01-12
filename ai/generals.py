# ai/generals_impl.py
from ai.general import General, Action
from core.map import Map
from core.unit import Unit
import random
import math

# (req 3)
class CaptainBRAINDEAD(General):
    """
    IA Niveau 0: Le bon capitaine revient d'une lobotomie réussie.
    Il n'est pas en état de donner des ordres tactiques.
    Les unités agissent individuellement : elles attaquent les ennemis
    dans leur champ de vision (Line of Sight) et s'en approchent si besoin,
    mais ne cherchent pas le combat si elles sont laissées seules.
    """
    def decide_actions(self, current_map: Map, my_units: list[Unit], enemy_units: list[Unit]) -> list[Action]:
        actions = []
        
        for unit in my_units:
            # 1. "Individual action": Recherche uniquement dans la ligne de vue de l'unité.
            # Contrairement à MajorDAFT, cette IA n'utilise JAMAIS la liste globale 'enemy_units'
            # pour trouver des cibles lointaines (pas de "seek out a fight").
            nearby_enemies = current_map.get_units_in_radius(unit.pos, unit.line_of_sight)
            
            # Filtre pour ne garder que les ennemis
            nearby_enemies = [e for e in nearby_enemies if e.army_id != self.army_id]

            if nearby_enemies:
                # 2. Si des ennemis sont visibles, l'unité engage le plus proche.
                closest_enemy = self.find_closest_enemy(unit, nearby_enemies)
                
                if closest_enemy:
                    if unit.can_attack(closest_enemy):
                        # L'unité attaque si elle est à portée.
                        actions.append(("attack", unit.unit_id, closest_enemy.unit_id))
                    else:
                        # L'unité s'approche pour engager l'ennemi qu'elle voit.
                        actions.append(("move", unit.unit_id, closest_enemy.pos))
        return actions

class MajorDAFT(General):
    """
    IA simple: s'approche de l'ennemi le plus proche et attaque.
    """
    def decide_actions(self, current_map: Map, my_units: list[Unit], enemy_units: list[Unit]) -> list[Action]:
        actions = []
        if not enemy_units:
            return []

        for unit in my_units:
            # Recherche optimisée dans la ligne de vue de l'unité
            nearby_enemies = current_map.get_units_in_radius(unit.pos, unit.line_of_sight)
            
            # Filtre pour ne garder que les vrais ennemis
            nearby_enemies = [e for e in nearby_enemies if e.army_id != self.army_id]

            if not nearby_enemies:
                # Si personne n'est visible, cherche l'ennemi le plus proche sur toute la carte
                closest_enemy = self.find_closest_enemy(unit, enemy_units)
            else:
                # Sinon, se concentre sur l'ennemi visible le plus proche
                closest_enemy = self.find_closest_enemy(unit, nearby_enemies)

            if not closest_enemy:
                continue

            if closest_enemy and unit.can_attack(closest_enemy):
                actions.append(("attack", unit.unit_id, closest_enemy.unit_id))
            else:
                actions.append(("move", unit.unit_id, closest_enemy.pos))
                
        return actions

class ColonelKAISER(General):
    """
    IA Stratégique (Req 3).
    - Évaluation des menaces (counters)
    - Formations (archers derrière)
    - Kiting pour les unités à distance
    - Focus fire intelligent
    - Synchronisation de l'avance (attend le regroupement)
    """
    # Constantes pour la configuration de l'IA
    KITING_RANGE_PERCENTAGE = 0.5  # Les unités à distance fuient si un ennemi est à 50% de leur portée
    MELEE_ATTACK_RANGE = 2  # Portée maximale pour être considéré comme une unité de mêlée
    RANGED_FORMATION_OFFSET = 3  # Les unités à distance restent à 3 unités derrière le front de mêlée
    TARGET_EVALUATION_RANGE_MULTIPLIER = 1.5  # Ne considère que les cibles dans 150% de la ligne de vue
    LOW_HP_BONUS_MULTIPLIER = 1.5  # Bonus de score pour attaquer les cibles qui peuvent être tuées en 2 coups
    EPSILON = 0.1  # Pour éviter la division par zéro
    FORMATION_COHESION_RADIUS = 8  # Rayon maximum pour considérer l'armée regroupée
    RANGED_BEHIND_MELEE_DISTANCE = 4  # Distance à laquelle les tireurs restent derrière les mêlées

    def __init__(self, army_id: int):
        super().__init__(army_id)
        self.target_memory: dict[int, int] = {}

    def _is_army_regrouped(self, my_units: list[Unit], centroid: tuple[float, float]) -> bool:
        """Vérifie si toutes les unités sont suffisamment proches du centroid."""
        for unit in my_units:
            dist = math.sqrt((unit.pos[0] - centroid[0])**2 + (unit.pos[1] - centroid[1])**2)
            if dist > self.FORMATION_COHESION_RADIUS:
                return False
        return True

    def _get_melee_front_position(self, melee_units: list[Unit], enemy_units: list[Unit]) -> tuple[float, float] | None:
        """Calcule la position du front de mêlée (centroid des mêlées)."""
        if not melee_units:
            return None
        avg_x = sum(u.pos[0] for u in melee_units) / len(melee_units)
        avg_y = sum(u.pos[1] for u in melee_units) / len(melee_units)
        return (avg_x, avg_y)

    def decide_actions(self, current_map: Map, my_units: list[Unit], enemy_units: list[Unit]) -> list[Action]:
        actions = []
        if not enemy_units or not my_units:
            return []

        enemy_lookup = {u.unit_id: u for u in enemy_units}

        melee_units = [u for u in my_units if u.attack_range <= self.MELEE_ATTACK_RANGE]
        ranged_units = [u for u in my_units if u.attack_range > self.MELEE_ATTACK_RANGE]

        avg_pos_x = sum(u.pos[0] for u in my_units) / len(my_units)
        avg_pos_y = sum(u.pos[1] for u in my_units) / len(my_units)
        army_centroid = (avg_pos_x, avg_pos_y)

        # Calculer la position du front de mêlée
        melee_front = self._get_melee_front_position(melee_units, enemy_units)

        # Vérifier si l'armée est regroupée
        is_regrouped = self._is_army_regrouped(my_units, army_centroid)

        # Trouver l'ennemi le plus proche globalement pour déterminer la direction d'avance
        closest_global_enemy = self.find_closest_enemy(Unit.__new__(Unit), enemy_units) if enemy_units else None
        if closest_global_enemy is None and enemy_units:
            closest_global_enemy = enemy_units[0]

        for unit in my_units:
            # Gestion du kiting pour les unités à distance
            if unit in ranged_units:
                threat_candidates = current_map.get_units_in_radius(unit.pos, unit.line_of_sight)
                threat = self.find_closest_enemy(unit, threat_candidates)
                if threat:
                    dist = unit._calculate_distance(threat)
                    safety_distance = unit.attack_range * self.KITING_RANGE_PERCENTAGE

                    if dist < safety_distance and threat.attack_range <= self.MELEE_ATTACK_RANGE:
                        flee_pos = self._calculate_flee_position(unit, threat)
                        actions.append(("move", unit.unit_id, flee_pos))
                        continue

            target = self._find_best_target(unit, enemy_units, enemy_lookup, current_map)

            if target:
                if unit.can_attack(target):
                    # L'unité peut attaquer, elle attaque !
                    actions.append(("attack", unit.unit_id, target.unit_id))
                else:
                    # L'unité ne peut pas attaquer, décision de mouvement
                    if unit in melee_units:
                        if is_regrouped:
                            # L'armée est regroupée, les mêlées avancent
                            actions.append(("move", unit.unit_id, target.pos))
                        else:
                            # L'armée n'est pas regroupée, les mêlées attendent au centroid
                            dist_to_centroid = math.sqrt((unit.pos[0] - army_centroid[0])**2 + (unit.pos[1] - army_centroid[1])**2)
                            if dist_to_centroid > 1:  # Si pas encore au centroid
                                actions.append(("move", unit.unit_id, army_centroid))
                            # Sinon, reste sur place (pas d'action)
                    elif unit in ranged_units:
                        # Les tireurs restent derrière le front de mêlée
                        if melee_front and closest_global_enemy:
                            move_pos = self._calculate_ranged_formation_position(unit, melee_front, closest_global_enemy)
                            actions.append(("move", unit.unit_id, move_pos))
                        else:
                            # Pas de front de mêlée, se positionner en retrait du centroid
                            move_pos = self._calculate_formation_position(unit, target, army_centroid)
                            actions.append(("move", unit.unit_id, move_pos))
            else:
                # Fallback: Avancer vers l'ennemi le plus proche si aucun visible
                closest_any = self.find_closest_enemy(unit, enemy_units)
                if closest_any:
                    if unit in melee_units and not is_regrouped:
                        # Attendre le regroupement
                        dist_to_centroid = math.sqrt((unit.pos[0] - army_centroid[0])**2 + (unit.pos[1] - army_centroid[1])**2)
                        if dist_to_centroid > 1:
                            actions.append(("move", unit.unit_id, army_centroid))
                    else:
                        actions.append(("move", unit.unit_id, closest_any.pos))
                else:
                    actions.append(("move", unit.unit_id, army_centroid))

        return actions

    def _find_best_target(self, unit: Unit, enemy_units: list[Unit], enemy_lookup: dict, current_map: Map) -> Unit | None:
        """
        Sélectionne la meilleure cible selon une heuristique de 'valeur'.
        Score = (Dégâts infligés / Dégâts reçus) * Bonus de proximité * Bonus Kill
        """
        best_target = None
        max_score = -1

        if unit.unit_id in self.target_memory:
            candidate = enemy_lookup.get(self.target_memory[unit.unit_id])
            if candidate and candidate.is_alive:
                return candidate
            else:
                del self.target_memory[unit.unit_id]

        # Limiter la recherche aux unités proches (spatial partition via la map)
        search_radius = unit.line_of_sight * self.TARGET_EVALUATION_RANGE_MULTIPLIER
        nearby_candidates = current_map.get_nearby_units(unit, search_radius)
        for enemy in nearby_candidates:
            if not enemy.is_alive or enemy.army_id == unit.army_id:
                continue

            dist = unit._calculate_distance(enemy)

            my_damage = unit.calculate_damage(enemy, current_map)
            enemy_damage = enemy.calculate_damage(unit, current_map)
            score = my_damage / (enemy_damage + self.EPSILON)

            proximity_bonus = 1 / (1 + dist)
            final_score = score * proximity_bonus

            if enemy.current_hp < my_damage * 2:
                final_score *= self.LOW_HP_BONUS_MULTIPLIER

            if final_score > max_score:
                max_score = final_score
                best_target = enemy

        if best_target:
            self.target_memory[unit.unit_id] = best_target.unit_id

        return best_target

    def _calculate_flee_position(self, unit: Unit, threat: Unit) -> tuple[float, float]:
        dx = unit.pos[0] - threat.pos[0]
        dy = unit.pos[1] - threat.pos[1]
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0: dist = self.EPSILON

        nx = unit.pos[0] + (dx / dist) * unit.speed
        ny = unit.pos[1] + (dy / dist) * unit.speed
        return (nx, ny)

    def _calculate_formation_position(self, unit: Unit, target: Unit, army_centroid: tuple) -> tuple[float, float]:
        dir_x = target.pos[0] - army_centroid[0]
        dir_y = target.pos[1] - army_centroid[1]
        dist = math.sqrt(dir_x**2 + dir_y**2)
        if dist == 0: dist = self.EPSILON

        pos_x = army_centroid[0] + (dir_x / dist) * (dist - self.RANGED_FORMATION_OFFSET)
        pos_y = army_centroid[1] + (dir_y / dist) * (dist - self.RANGED_FORMATION_OFFSET)

        return (pos_x, pos_y)

    def _calculate_ranged_formation_position(self, unit: Unit, melee_front: tuple[float, float], enemy: Unit) -> tuple[float, float]:
        """
        Calcule la position pour une unité à distance: derrière le front de mêlée, 
        en restant à une distance RANGED_BEHIND_MELEE_DISTANCE dans la direction opposée à l'ennemi.
        """
        # Direction du front de mêlée vers l'ennemi
        dir_x = enemy.pos[0] - melee_front[0]
        dir_y = enemy.pos[1] - melee_front[1]
        dist = math.sqrt(dir_x**2 + dir_y**2)
        if dist == 0: 
            dist = self.EPSILON
        
        # Normaliser la direction
        norm_x = dir_x / dist
        norm_y = dir_y / dist
        
        # Position derrière le front de mêlée (direction opposée à l'ennemi)
        pos_x = melee_front[0] - norm_x * self.RANGED_BEHIND_MELEE_DISTANCE
        pos_y = melee_front[1] - norm_y * self.RANGED_BEHIND_MELEE_DISTANCE
        
        return (pos_x, pos_y)