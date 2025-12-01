# engine.py
import math
from typing import Optional, Any
from core.map import Map  # Suppose que Map est dans core/map.py
from core.army import Army  # Suppose que Army est dans core/army.py
from core.unit import Unit
from ai.general import General  # Suppose que General est dans ai/general.py

# Type alias pour les actions que l'IA peut retourner
# Format: ("commande", id_unite, data)
# ex: ("move", 1, (10.5, 4.2))
# ex: ("attack", 1, 2)  (unité 1 attaque unité 2)
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
        self.winner: Optional[int] = None # army_id du vainqueur

        self.paused: bool = False

        # Dictionnaire central pour accès O(1) aux unités (sec 24.4)
        self.units_by_id: dict[int, Unit] = {}
        for army in self.armies:
            for unit in army.units:
                if unit.unit_id in self.units_by_id:
                    # Gère un ID en double, crucial pour le débogage
                    raise ValueError(f"Erreur: ID d'unité {unit.unit_id} dupliqué.")
                self.units_by_id[unit.unit_id] = unit
                # Ajoute l'unité à la matrice creuse
                self.map.add_unit(unit)

    def run_game(self, max_turns: int = 1000, view: Any = None):
        """Boucle de jeu principale avec gestion de la vitesse et de la pause."""
        print(f"Début de la partie sur une carte de {self.map.width}x{self.map.height}!")

        frame_counter = 0
        # Vitesse : Plus c'est haut, plus c'est lent.
        LOGIC_SPEED_DIVIDER = 15
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
            # On ne continue que si :
            # - Le jeu n'est PAS en pause
            # - OU BIEN on a demandé un "step_once" (touche S)
            if self.paused and not step_once:
                continue

            # --- 3. Ralentissement de la logique (si pas en mode step) ---
            frame_counter += 1
            if not step_once and frame_counter % LOGIC_SPEED_DIVIDER != 0:
                continue
            
            # Réinitialiser le flag de pas-à-pas
            step_once = False

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
            # Dernier affichage avant de quitter
            view.display(self.armies, self.turn_count, self.paused)
    def _execute_actions(self, actions: list[Action]):
        """Exécute les actions (Mouvements PUIS Attaques)."""

        # 1. Mouvements (Prioritaires)
        for action_type, unit_id, data in actions:
            if action_type == "move":
                unit = self.units_by_id.get(unit_id)
                target_pos = data
                if unit and unit.is_alive:
                    self._handle_movement(unit, target_pos)

        # 2. Attaques (Après tous les mouvements)
        for action_type, unit_id, data in actions:
            if action_type == "attack":
                unit = self.units_by_id.get(unit_id)
                target_id = data
                target = self.units_by_id.get(target_id)

                if unit and unit.is_alive and target and target.is_alive:
                    unit.attack(target, self.map)

    def _handle_movement(self, unit: Unit, target_pos: tuple[float, float]):
        """Calcule et applique le mouvement d'une unité vers une cible flottante."""

        old_pos = unit.pos
        vector_x = target_pos[0] - old_pos[0]
        vector_y = target_pos[1] - old_pos[1]

        distance = math.sqrt(vector_x**2 + vector_y**2)

        if distance < 0.01:
            return

        move_dist = min(distance, unit.speed)

        if distance > 0:
            norm_x = vector_x / distance
            norm_y = vector_y / distance
            potential_pos = (
                old_pos[0] + norm_x * move_dist,
                old_pos[1] + norm_y * move_dist
            )
        else:
            potential_pos = old_pos

        # --- Collision Detection ---
        final_pos = self._resolve_collisions(unit, potential_pos)

        # --- CORRECTION : Collision avec les Bords de la Map ---
        # On contraint x entre 0 et map.width
        # On contraint y entre 0 et map.height
        # On laisse une petite marge (ex: 0.1) pour ne pas être pile sur la ligne
        x = max(0.1, min(final_pos[0], self.map.width - 0.1))
        y = max(0.1, min(final_pos[1], self.map.height - 0.1))
        
        final_pos = (x, y)

        self.map.update_unit_position(unit, old_pos, final_pos)

    def _resolve_collisions(self, moving_unit: Unit, potential_pos: tuple[float, float]) -> tuple[float, float]:
        """
        Vérifie les collisions à la `potential_pos` et ajuste la position finale.
        """
        final_pos = potential_pos

        # Recherche optimisée des unités proches grâce à la Map
        nearby_units = self.map.get_nearby_units(moving_unit, search_radius=moving_unit.hitbox_radius * 2)

        for other_unit in nearby_units:
            if other_unit == moving_unit:
                continue

            # Calcul de la distance entre les centres
            dist_centers = math.sqrt(
                (final_pos[0] - other_unit.pos[0])**2 +
                (final_pos[1] - other_unit.pos[1])**2
            )

            # Somme des rayons des hitbox
            sum_radii = moving_unit.hitbox_radius + other_unit.hitbox_radius

            # S'il y a collision (chevauchement)
            if dist_centers < sum_radii:
                overlap = sum_radii - dist_centers

                if dist_centers == 0: # Éviter la division par zéro si superposés
                    final_pos = (final_pos[0] + 0.01, final_pos[1])
                    dist_centers = 0.01

                # Repousser l'unité en mouvement dans la direction opposée
                push_x = (final_pos[0] - other_unit.pos[0]) / dist_centers
                push_y = (final_pos[1] - other_unit.pos[1]) / dist_centers

                final_pos = (
                    final_pos[0] + push_x * overlap,
                    final_pos[1] + push_y * overlap
                )

        return final_pos

    def _reap_dead_units(self):
        """Retire les unités mortes de la simulation active."""
        # On itère sur une copie de la liste des clés (sec 24.4)
        for unit_id in list(self.units_by_id.keys()):
            unit = self.units_by_id.get(unit_id)
            if unit and not unit.is_alive:
                print(f"{unit} est retiré du champ de bataille.")
                self.map.remove_unit(unit) # Retirer de la matrice creuse
                del self.units_by_id[unit_id] # Retirer du lookup

    def _check_game_over(self) -> bool:
        """Vérifie si une des armées a été éliminée."""
        army1_defeated = self.armies[0].is_defeated()
        army2_defeated = self.armies[1].is_defeated()

        if army1_defeated and army2_defeated:
            self.game_over = True
            self.winner = None # Égalité
        elif army1_defeated:
            self.game_over = True
            self.winner = self.armies[1].army_id
        elif army2_defeated:
            self.game_over = True
            self.winner = self.armies[0].army_id

        return self.game_over

    def get_enemy_units(self, my_army_id: int) -> list[Unit]:
        """Récupère les unités ennemies vivantes."""
        enemies = []
        for unit in self.units_by_id.values():
            if unit.army_id != my_army_id:
                enemies.append(unit)
        return enemies