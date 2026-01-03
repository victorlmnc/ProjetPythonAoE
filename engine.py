# engine.py
import math
import os
from typing import Optional, Any
from core.map import Map
from core.army import Army
from core.unit import Unit
from ai.general import General

# Type alias pour les actions que l'IA peut retourner
Action = tuple[str, int, Any]

# Chemin par défaut pour les sauvegardes rapides (F11/F12)
QUICK_SAVE_PATH = "saves/quicksave.sav"

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

        # Optimisation : Set des obstacles pour recherche O(1)
        self.obstacle_set = set((x, y) for _, x, y in self.map.obstacles)

        for army in self.armies:
            for unit in army.units:
                if unit.unit_id in self.units_by_id:
                    raise ValueError(f"Erreur: ID d'unité {unit.unit_id} dupliqué.")
                self.units_by_id[unit.unit_id] = unit
                self.map.add_unit(unit)

    def run_game(self, max_turns: int = 1000, view: Optional[Any] = None, logic_speed: int = 15):
        """
        Boucle principale du jeu.
        """
        print(f"Début de la partie sur une carte de {self.map.width}x{self.map.height}!")

        frame_counter = 0
        # Vitesse de la logique : Plus ce chiffre est haut, plus le jeu est lent.
        # 15 donne un bon rythme visible à 60 FPS (4 ticks logique / sec).
        LOGIC_SPEED_DIVIDER = logic_speed
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
                elif command == "quick_save":
                    # F11 - Sauvegarde rapide (Requis par le PDF)
                    # Import local pour éviter l'import circulaire
                    from utils.serialization import save_game
                    os.makedirs("saves", exist_ok=True)
                    save_game(self, QUICK_SAVE_PATH)
                    print("Sauvegarde rapide effectuée !")
                elif command == "quick_load":
                    # F12 - Chargement rapide (Requis par le PDF)
                    # Note: Le chargement complet nécessite une refonte de la boucle
                    print("Quick Load: Utilisez 'battle --load_game saves/quicksave.sav' pour charger.")
                elif command == "switch_view":
                    # F9 - Basculer entre vues (pour info, nécessiterait une refonte)
                    print("Switch View: Non implémenté (nécessite de relancer avec -t)")
                elif command == "speed_up":
                    LOGIC_SPEED_DIVIDER = max(1, LOGIC_SPEED_DIVIDER - 2)
                    print(f"Vitesse++ (Divider: {LOGIC_SPEED_DIVIDER})")
                elif command == "speed_down":
                    LOGIC_SPEED_DIVIDER = min(60, LOGIC_SPEED_DIVIDER + 2)
                    print(f"Vitesse-- (Divider: {LOGIC_SPEED_DIVIDER})")

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
                # Mettre à jour l'animation par unité (ms)
                try:
                    unit.tick_animation(int(TIME_STEP * 1000))
                except Exception:
                    pass

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
                    if unit.can_attack(target) and unit.can_act():
                        final_damage = unit.calculate_damage(target, self.map)
                        target.take_damage(final_damage)
                        unit.current_cooldown = unit.reload_time
                        
                        # --- Splash Damage (Onager, Trebuchet) ---
                        if hasattr(unit, 'splash_radius') and unit.splash_radius > 0:
                            splash_damage = int(final_damage * 0.5)  # 50% des dégâts
                            for other in self.units_by_id.values():
                                if other.is_alive and other != target and other.army_id != unit.army_id:
                                    dist = math.sqrt((other.pos[0] - target.pos[0])**2 + 
                                                    (other.pos[1] - target.pos[1])**2)
                                    if dist <= unit.splash_radius:
                                        other.take_damage(splash_damage)
                        
                        # --- Trample Damage (Elite War Elephant) ---
                        if hasattr(unit, 'trample_radius') and unit.trample_radius > 0:
                            trample_dmg = int(final_damage * getattr(unit, 'trample_damage_ratio', 0.5))
                            for other in self.units_by_id.values():
                                if other.is_alive and other != target and other.army_id != unit.army_id:
                                    dist = math.sqrt((other.pos[0] - unit.pos[0])**2 + 
                                                    (other.pos[1] - unit.pos[1])**2)
                                    if dist <= unit.trample_radius:
                                        other.take_damage(trample_dmg)
        
        # 3. Actions spéciales des Moines (Heal / Conversion) - PDF Req 6
        for action_type, unit_id, data in actions:
            unit = self.units_by_id.get(unit_id)
            if not unit or not unit.is_alive:
                continue
            
            # Le Monk a des attributs spéciaux
            if not hasattr(unit, 'heal_rate'):
                continue
            
            if action_type == "heal":
                # Soigner une unité alliée
                target = self.units_by_id.get(data)
                if target and target.is_alive and target.army_id == unit.army_id:
                    if unit.can_act():
                        heal_amount = unit.heal_rate
                        target.current_hp = min(target.max_hp, target.current_hp + heal_amount)
                        unit.current_cooldown = unit.reload_time
            
            elif action_type == "convert":
                # Tenter de convertir une unité ennemie
                target = self.units_by_id.get(data)
                if target and target.is_alive and target.army_id != unit.army_id:
                    distance = math.sqrt((unit.pos[0] - target.pos[0])**2 + 
                                        (unit.pos[1] - target.pos[1])**2)
                    if distance <= getattr(unit, 'conversion_range', 9.0) and unit.can_act():
                        # Conversion réussie (simplifié : toujours réussie après cooldown)
                        # Changer l'armée de l'unité convertie
                        old_army_id = target.army_id
                        target.army_id = unit.army_id
                        unit.current_cooldown = getattr(unit, 'conversion_time', 4.0)
                        print(f"CONVERSION: {unit} a converti {target}!")

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

        # --- Gestion des Obstacles (Sliding) ---
        if self._is_colliding_with_obstacle(potential_pos, unit.hitbox_radius):
            # Tentative de glissement en X
            test_pos_x = (potential_pos[0], old_pos[1])
            can_move_x = not self._is_colliding_with_obstacle(test_pos_x, unit.hitbox_radius)

            # Tentative de glissement en Y
            test_pos_y = (old_pos[0], potential_pos[1])
            can_move_y = not self._is_colliding_with_obstacle(test_pos_y, unit.hitbox_radius)

            if can_move_x and can_move_y:
                # Si on peut glisser des deux côtés, on prend celui qui conserve le plus de mouvement
                if abs(vector_x) > abs(vector_y):
                     potential_pos = test_pos_x
                else:
                     potential_pos = test_pos_y
            elif can_move_x:
                potential_pos = test_pos_x
            elif can_move_y:
                potential_pos = test_pos_y
            else:
                # Bloqué complètement
                potential_pos = old_pos

        # --- Collision Detection (Unités) ---
        final_pos = self._resolve_collisions(unit, potential_pos)

        # --- Collision avec les Bords de la Map (CORRECTION) ---
        x = max(0.1, min(final_pos[0], self.map.width - 0.1))
        y = max(0.1, min(final_pos[1], self.map.height - 0.1))
        final_pos = (x, y)

        self.map.update_unit_position(unit, old_pos, final_pos)

    def _is_colliding_with_obstacle(self, pos: tuple[float, float], radius: float) -> bool:
        """Vérifie si une position chevauche un obstacle de la carte."""
        min_x = int(pos[0] - radius)
        max_x = int(pos[0] + radius)
        min_y = int(pos[1] - radius)
        max_y = int(pos[1] + radius)

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                if (x, y) in self.obstacle_set:
                    return True
        return False

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
        """
        Vérifie les conditions de fin de partie.
        Conditions de victoire (PDF):
        1. Destruction de la Merveille (Wonder) ennemie = Victoire immédiate
        2. Élimination de toutes les unités ennemies
        """
        # Import local pour éviter les imports circulaires
        from core.unit import Wonder
        
        # Vérification de la destruction des Wonders (Condition prioritaire selon PDF)
        for army_idx, army in enumerate(self.armies):
            enemy_idx = 1 - army_idx  # L'autre armée
            
            # Vérifier si l'armée ennemie avait une Wonder et si elle est morte
            for unit in self.armies[enemy_idx].units:
                if isinstance(unit, Wonder) and not unit.is_alive:
                    # La Wonder ennemie est détruite -> Victoire !
                    self.game_over = True
                    self.winner = army.army_id
                    print(f"La Wonder de l'Armée {enemy_idx} a été détruite !")
                    return True
        
        # Vérification standard: élimination de toutes les unités
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