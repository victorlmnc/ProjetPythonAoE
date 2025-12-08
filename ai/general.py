# ai/general.py
from core.map import Map
from core.unit import Unit
from typing import Optional
import abc # (Utilisation de classes abstraites, sec 27)

# Type alias pour les actions
type Action = tuple[str, int, any]

class General(abc.ABC):
    """
    Classe de base abstraite pour une IA (req 3).
    Doit implémenter 'decide_actions'.
    """
    def __init__(self, army_id: int):
        self.army_id = army_id
    
    @abc.abstractmethod
    def decide_actions(self, current_map: Map, my_units: list[Unit], enemy_units: list[Unit]) -> list[Action]:
        """
        L'IA doit retourner une liste d'actions pour ses unités.
        """
        pass

    def find_closest_enemy(self, unit: Unit, enemy_units: list[Unit]) -> Optional[Unit]:
        """
        Une fonction utilitaire que les IA peuvent réutiliser.
        """
        closest_enemy = None
        min_dist = float('inf') # (sec 22.2.1)

        for enemy in enemy_units:
            if not enemy.is_alive:
                continue
            
            # Utilise la distance Euclidienne (privée, mais ok pour l'exemple)
            dist = unit._calculate_distance(enemy)
            if dist < min_dist:
                min_dist = dist
                closest_enemy = enemy
        
        return closest_enemy