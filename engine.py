# engine.py
import math
from typing import Optional, Any
from core.map import Map
from core.army import Army
from core.unit import Unit
from ai.general import General

# Type alias pour les actions que l'IA peut retourner
Action = tuple[str, int, Any]

class Engine:
    """
    Le moteur de jeu principal (req 5).
    Gère la boucle de jeu, l'état du monde, et met à jour la
    matrice creuse (la Map) avec les positions flottantes.
    """
    def __init__(self, map_instance: Map, army1: Army, army2: Army):
        self.map: Map = map_instance
        self.armies: list[Army] = [army1, army2]
        self.turn_count: int = 0
        self.game_over: bool = False
        self.winner: Optional[int] = None 
        
        # État de pause pour l'interface
        self.paused: bool = False 

        # Dictionnaire central pour accès O(1) aux unités
        self.units_by_id: dict[int, Unit] = {}
        for army in self.armies:
            for unit in army.units:
                if unit.unit_id in self.units_by_id:
                    raise ValueError(f"Erreur: ID d'unité {unit.unit_id} dupliqué.")
                self.units_by_id[unit.unit_id] = unit
                self.map.add_unit(unit)

    def run_game(self, max_turns: int = 1000, view: Any = None):
        """Boucle de jeu principale avec gestion de la vitesse et de la pause."""
        print(f"Début de la partie sur une carte de {self.map.width}x{self.map.height}!")

        frame_counter = 0
        # Vitesse de la logique : Plus ce chiffre est haut, plus le jeu est lent.
        # 5 est un bon équilibre à 60 FPS (12 ticks logique / sec).
        LOGIC_SPEED_DIVIDER = 5
        step_once = False # Pour le mode pas-à-pas (touche S)

        while not self.game_over and self.turn_count < max_turns:
            
            # --- 1. Gestion des Inputs et Affichage ---
            if view:
                # La vue nous renvoie des commandes (pause, step, quit)
                command = view.display(self.armies, self.turn_count, self.paused)
                
                if command == "quit":
                    break
                elif command == "toggle_pause":
                    self.paused = not self.paused
                    print(f"Jeu {'en PAUSE' if self.paused else 'REPRIS'}")
                elif command == "step":
                    self.paused = True # Le pas-à-pas force la pause après
                    step_once = True

            elif self.turn_count % 10 == 0:
                print(f"\n--- TOUR {self.turn_count} ---")

            # --- 2. Blocage si en pause ---
            if self.paused and not step_once:
                continue

            # --- 3. Ralentissement de la logique (si pas en mode step) ---
            frame_counter += 1
            if not step_once and frame_counter % LOGIC_SPEED_DIVIDER != 0:
                continue
            
            step_once = False # Reset du step

            # --- DÉBUT DE LA LOGIQUE DU TOUR ---
            self._reap_dead_units()

            if self._check_game_over():
                break

            all_actions: list[Action] = []
            for army in self.armies:
                if not army.is_defeated():
                    my_living_units = [u for u in army.units if u.is_alive]
                    enemy_living_units = self.get_enemy_units(army.army_id)
                    if not enemy_living_units: continue

                    actions = army.general.decide_actions(self.map, my_living_units, enemy_living_units)
                    all_actions.extend(actions)

            self._execute_actions(all_actions)
            self.turn_count += 1
            # --- FIN DE LA LOGIQUE ---

        if view:
            view.display(self.armies, self.turn_count, self.paused)

        print("\n--- FIN DE LA PARTIE ---")
        if self.winner is not None:
            print(f"Le vainqueur est l'Armée {self.winner}!")
        elif self.turn_count >= max_turns:
            print("Limite de tours atteinte. Égalité.")
        else:
            print("Égalité.")

    def _execute_actions(self, actions: list[Action]):
        """Exécute les actions (Temps, Mouvements, Attaques)."""

        # 0. FAIRE AVANCER LE TEMPS (COOLDOWNS)
        # On considère qu'un tick logique = 0.5 sec de temps de jeu (arbitraire)
        TIME_STEP = 0.5 
        for unit in self.units_by_id.values():
            if unit.is_alive:
                unit.tick_cooldown(TIME_STEP)

        # 1. Mouvements (Prioritaires)
        for action_type, unit_id, data in actions:
            if action_type == "move":
                unit = self.units_by_id.get(unit_id)
                target_pos = data
                if unit and unit.is_alive:
                    self._handle_movement(unit, target_pos)

        # 2. Attaques (Après mouvements)
        for action_type, unit_id, data in actions:
            if action_type == "attack":
                unit = self.units_by_id.get(unit_id)
                target_id = data
                target = self.units_by_id.get(target_id)

                if unit and unit.is_alive and target and target.is_alive:
                    # L'unité vérifie son cooldown interne ici
                    unit.attack(target, self.map)

    def _handle_movement(self, unit: Unit, target_pos: tuple[float, float]):
        """Calcule et applique le mouvement."""
        old_pos = unit.pos
        vector_x = target_pos[0] - old_pos[0]
        vector_y = target_pos[1] - old_pos[1]
        distance = math.sqrt(vector_x**2 + vector_y**2)

        if distance < 0.01: return

        move_dist = min(distance, unit.speed)
        norm_x = vector_x / distance
        norm_y = vector_y / distance
        potential_pos = (old_pos[0] + norm_x * move_dist, old_pos[1] + norm_y * move_dist)

        # --- Collision Detection (Unités) ---
        final_pos = self._resolve_collisions(unit, potential_pos)

        # --- Collision avec les Bords de la Map (CORRECTION) ---
        x = max(0.1, min(final_pos[0], self.map.width - 0.1))
        y = max(0.1, min(final_pos[1], self.map.height - 0.1))
        final_pos = (x, y)

        self.map.update_unit_position(unit, old_pos, final_pos)

    def _resolve_collisions(self, moving_unit: Unit, potential_pos: tuple[float, float]) -> tuple[float, float]:
        """Gère le chevauchement des unités."""
        final_pos = potential_pos
        nearby_units = self.map.get_nearby_units(moving_unit, search_radius=moving_unit.hitbox_radius * 2)

        for other_unit in nearby_units:
            if other_unit == moving_unit: continue

            dist_centers = math.sqrt((final_pos[0] - other_unit.pos[0])**2 + (final_pos[1] - other_unit.pos[1])**2)
            sum_radii = moving_unit.hitbox_radius + other_unit.hitbox_radius

            if dist_centers < sum_radii:
                overlap = sum_radii - dist_centers
                if dist_centers == 0: 
                    dist_centers = 0.01
                    final_pos = (final_pos[0] + 0.01, final_pos[1])

                push_x = (final_pos[0] - other_unit.pos[0]) / dist_centers
                push_y = (final_pos[1] - other_unit.pos[1]) / dist_centers
                final_pos = (final_pos[0] + push_x * overlap, final_pos[1] + push_y * overlap)

        return final_pos

    def _reap_dead_units(self):
        """Retire les unités mortes."""
        for unit_id in list(self.units_by_id.keys()):
            unit = self.units_by_id.get(unit_id)
            if unit and not unit.is_alive:
                self.map.remove_unit(unit)
                del self.units_by_id[unit_id]

    def _check_game_over(self) -> bool:
        army1_defeated = self.armies[0].is_defeated()
        army2_defeated = self.armies[1].is_defeated()
        if army1_defeated and army2_defeated:
            self.game_over = True
            self.winner = None
        elif army1_defeated:
            self.game_over = True
            self.winner = self.armies[1].army_id
        elif army2_defeated:
            self.game_over = True
            self.winner = self.armies[0].army_id
        return self.game_over

    def get_enemy_units(self, my_army_id: int) -> list[Unit]:
        return [u for u in self.units_by_id.values() if u.army_id != my_army_id]