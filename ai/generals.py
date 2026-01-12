# ai/generals_impl.py
from ai.general import General, Action
from core.map import Map
from core.unit import Unit, Crossbowman
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
# (req 3)
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
    IA Stratégique Avancée - Version 2.0: Plus agressive et cohésive.
    
    Principes:
    - Marche groupée vers l'ennemi (pas de fuite excessive)
    - Formation en ligne: Mêlée devant, Distance derrière
    - Focus fire: Concentrer les attaques sur les cibles faibles
    - Priorité aux kills: Finir les unités blessées
    """
    
    # === CONFIGURATION ===
    MELEE_THRESHOLD = 2.0  # En dessous = unité de mêlée
    FORMATION_SPACING = 1.8  # Espacement entre unités
    ENGAGE_RANGE = 12.0  # Distance pour ignorer la formation et charger
    
    def __init__(self, army_id: int):
        super().__init__(army_id)
        # Mémoire des cibles pour éviter le switch permanent
        self.target_memory: dict[int, int] = {}
        
    def decide_actions(self, current_map: Map, my_units: list[Unit], enemy_units: list[Unit]) -> list[Action]:
        """Décide des actions pour toutes les unités de l'armée."""
        if not my_units or not enemy_units:
            return []
        
        actions = []
        alive_enemies = [e for e in enemy_units if e.is_alive]
        if not alive_enemies:
            return []
        
        # === 1. ANALYSE STRATÉGIQUE ===
        army_center = self._get_army_center(my_units)
        enemy_center = self._get_army_center(alive_enemies)
        
        # Direction vers l'ennemi
        direction = self._normalize(
            enemy_center[0] - army_center[0],
            enemy_center[1] - army_center[1]
        )
        
        # Distance globale
        global_distance = math.sqrt(
            (enemy_center[0] - army_center[0])**2 + 
            (enemy_center[1] - army_center[1])**2
        )
        
        # === 2. SÉPARER MÊLÉE / DISTANCE ===
        melee_units = [u for u in my_units if u.attack_range <= self.MELEE_THRESHOLD]
        ranged_units = [u for u in my_units if u.attack_range > self.MELEE_THRESHOLD]
        
        # Trier par ID pour placement déterministe
        melee_units.sort(key=lambda u: u.unit_id)
        ranged_units.sort(key=lambda u: u.unit_id)
        
        # === 3. CALCULER LES SLOTS DE FORMATION ===
        formation_slots = self._calculate_line_formation(
            melee_units, ranged_units, army_center, direction
        )
        
        # === 4. IDENTIFIER LES CIBLES PRIORITAIRES (FOCUS FIRE) ===
        priority_targets = self._get_priority_targets(alive_enemies, my_units, current_map)
        
        # === 5. DÉCIDER POUR CHAQUE UNITÉ ===
        for unit in my_units:
            action = self._decide_unit_action(
                unit, alive_enemies, priority_targets, 
                formation_slots, direction, global_distance, current_map
            )
            if action:
                actions.append(action)
        
        return actions
    
    def _get_army_center(self, units: list[Unit]) -> tuple[float, float]:
        """Calcule le centre de masse d'un groupe d'unités."""
        if not units:
            return (0.0, 0.0)
        x = sum(u.pos[0] for u in units) / len(units)
        y = sum(u.pos[1] for u in units) / len(units)
        return (x, y)
    
    def _normalize(self, dx: float, dy: float) -> tuple[float, float]:
        """Normalise un vecteur direction."""
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < 0.001:
            return (1.0, 0.0)
        return (dx / dist, dy / dist)
    
    def _calculate_line_formation(
        self, 
        melee: list[Unit], 
        ranged: list[Unit], 
        center: tuple[float, float], 
        direction: tuple[float, float]
    ) -> dict[int, tuple[float, float]]:
        """
        Formation en LIGNE: Mêlée devant, Distance derrière.
        Bien aligné et visuellement propre.
        """
        slots = {}
        dx, dy = direction
        # Perpendiculaire (pour étaler la ligne)
        perp_x, perp_y = -dy, dx
        
        spacing = self.FORMATION_SPACING
        
        # === LIGNE DE MÊLÉE (DEVANT) ===
        n_melee = len(melee)
        for i, unit in enumerate(melee):
            # Centrer la ligne
            offset = (i - (n_melee - 1) / 2) * spacing
            # Position = centre + offset perpendiculaire + avance vers l'ennemi
            x = center[0] + perp_x * offset + dx * 2.0
            y = center[1] + perp_y * offset + dy * 2.0
            slots[unit.unit_id] = (x, y)
        
        # === LIGNE DE DISTANCE (DERRIÈRE) ===
        n_ranged = len(ranged)
        for i, unit in enumerate(ranged):
            offset = (i - (n_ranged - 1) / 2) * spacing
            # Derrière la mêlée (recul de 3 unités)
            x = center[0] + perp_x * offset - dx * 3.0
            y = center[1] + perp_y * offset - dy * 3.0
            slots[unit.unit_id] = (x, y)
        
        return slots
    
    def _get_priority_targets(
        self, 
        enemies: list[Unit], 
        my_units: list[Unit],
        current_map: Map
    ) -> list[Unit]:
        """
        Trie les ennemis par priorité pour focus fire.
        Priorité: Faible HP > Haute menace > Distance proche
        """
        if not enemies:
            return []
        
        # Calculer un score pour chaque ennemi
        scored = []
        my_center = self._get_army_center(my_units)
        
        for enemy in enemies:
            score = 0.0
            
            # Bonus ÉNORME pour les unités presque mortes (kill secure)
            hp_ratio = enemy.current_hp / enemy.max_hp
            if hp_ratio < 0.3:
                score += 100  # Priorité absolue
            elif hp_ratio < 0.5:
                score += 50
            
            # Bonus pour les unités à distance (archers = menace)
            if enemy.attack_range > self.MELEE_THRESHOLD:
                score += 20
            
            # Bonus pour la proximité
            dist = math.sqrt(
                (enemy.pos[0] - my_center[0])**2 + 
                (enemy.pos[1] - my_center[1])**2
            )
            score += max(0, 30 - dist)  # Plus proche = mieux
            
            # Malus pour les gros tanks (longs à tuer)
            if enemy.max_hp > 100:
                score -= 10
            
            scored.append((score, enemy))
        
        # Trier par score décroissant
        scored.sort(key=lambda x: -x[0])
        return [e for _, e in scored]
    
    def _decide_unit_action(
        self,
        unit: Unit,
        enemies: list[Unit],
        priority_targets: list[Unit],
        formation_slots: dict[int, tuple[float, float]],
        direction: tuple[float, float],
        global_distance: float,
        current_map: Map
    ) -> tuple | None:
        """Décide l'action d'une unité individuelle."""
        
        # === A. TROUVER LA MEILLEURE CIBLE ===
        target = self._select_target(unit, enemies, priority_targets, current_map)
        
        if not target:
            slot = formation_slots.get(unit.unit_id)
            if slot:
                return ("move", unit.unit_id, slot)
            return None
        
        # === B. PEUT ATTAQUER? → ATTAQUER! ===
        if unit.can_attack(target):
            return ("attack", unit.unit_id, target.unit_id)
        
        # === C. SINON → CHARGER VERS LA CIBLE ===
        # Pas de formation, pas de recul, juste ATTAQUER
        return ("move", unit.unit_id, target.pos)
    
    def _select_target(
        self, 
        unit: Unit, 
        enemies: list[Unit], 
        priority_targets: list[Unit],
        current_map: Map
    ) -> Unit | None:
        """
        Sélectionne la meilleure cible pour une unité.
        Utilise la mémoire pour éviter le switch permanent.
        """
        # Vérifier si on a déjà une cible valide
        if unit.unit_id in self.target_memory:
            old_target_id = self.target_memory[unit.unit_id]
            for enemy in enemies:
                if enemy.unit_id == old_target_id and enemy.is_alive:
                    # Garder cette cible si elle est encore raisonnable
                    dist = unit._calculate_distance(enemy)
                    if dist < unit.line_of_sight * 2:
                        return enemy
            # Cible invalide, oublier
            del self.target_memory[unit.unit_id]
        
        # Chercher parmi les cibles prioritaires
        for target in priority_targets:
            dist = unit._calculate_distance(target)
            # Préférer les cibles à portée ou proches
            if dist < unit.line_of_sight * 1.5:
                self.target_memory[unit.unit_id] = target.unit_id
                return target
        
        # Fallback: l'ennemi le plus proche
        closest = self.find_closest_enemy(unit, enemies)
        if closest:
            self.target_memory[unit.unit_id] = closest.unit_id
        return closest
