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
        """Boucle de jeu principale."""
        print(f"Début de la partie sur une carte de {self.map.width}x{self.map.height}!")
        
        while not self.game_over and self.turn_count < max_turns:
            
            if view:
                view.display(self.armies, self.turn_count)
            elif self.turn_count % 10 == 0:  
                print(f"\n--- TOUR {self.turn_count} ---")
            
            # 1. Nettoyer les unités mortes du tour précédent
            self._reap_dead_units()

            # 2. Vérifier si la partie est déjà finie (avant que les IA jouent)
            if self._check_game_over():
                break

            # 3. Prise de décision (IA)
            all_actions: list[Action] = []
            for army in self.armies:
                # L'armée ne joue pas si elle est vaincue
                if not army.is_defeated(): 
                    # Récupère les unités vivantes pour l'IA
                    my_living_units = [u for u in army.units if u.is_alive]
                    enemy_living_units = self.get_enemy_units(army.army_id)
                    
                    if not enemy_living_units:
                        continue # Plus d'ennemis à combattre

                    actions = army.general.decide_actions(
                        current_map=self.map,
                        my_units=my_living_units,
                        enemy_units=enemy_living_units
                    )
                    all_actions.extend(actions)
            
            # 4. Exécution des actions
            self._execute_actions(all_actions)
            
            self.turn_count += 1
        
        if view:
            view.display(self.armies, self.turn_count)
            
        # --- Fin de la boucle ---
        print("\n--- FIN DE LA PARTIE ---")
        if self.winner is not None:
            print(f"Le vainqueur est l'Armée {self.winner}!")
        elif self.turn_count >= max_turns:
            print("Limite de tours atteinte. Égalité.")
        else:
            print("Égalité (les deux armées ont perdu en même temps?).")

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
                    unit.attack(target)

    def _handle_movement(self, unit: Unit, target_pos: tuple[float, float]):
        """Calcule et applique le mouvement d'une unité vers une cible flottante."""
        
        old_pos = unit.pos
        vector_x = target_pos[0] - old_pos[0]
        vector_y = target_pos[1] - old_pos[1]
        
        # Distance (norme du vecteur)
        distance = math.sqrt(vector_x**2 + vector_y**2)
        
        if distance < 0.01:
            return # Déjà sur place (ou presque)

        # Si la distance est inférieure à la vitesse, on arrive à destination
        if distance <= unit.speed:
            new_pos = target_pos
        else:
            # Normalisation du vecteur (le rendre de longueur 1)
            norm_x = vector_x / distance
            norm_y = vector_y / distance
            
            # Calcul de la nouvelle position en flottant
            new_pos = (
                old_pos[0] + norm_x * unit.speed,
                old_pos[1] + norm_y * unit.speed
            )
        
        # **CRUCIAL**: Notifier la Map (matrice creuse) du changement
        # La fonction update_unit_position met à jour unit.pos elle-même
        self.map.update_unit_position(unit, old_pos, new_pos)
        
        # print(f"{unit} se déplace vers {new_pos}") # Optionnel (très verbeux)

    def _reap_dead_units(self):
        """Retire les unités mortes de la simulation active."""
        # On itère sur une copie de la liste des clés (sec 24.4)
        for unit_id in list(self.units_by_id.keys()):
            unit = self.units_by_id[unit_id]
            if not unit.is_alive:
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