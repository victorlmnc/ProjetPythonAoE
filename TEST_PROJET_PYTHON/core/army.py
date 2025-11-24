# core/army.py
from core.unit import Unit
from ai.general import General

class Army:
    """
    Représente une armée (req 4).
    Contient une liste d'unités et le Général (IA) qui les commande.
    """
    def __init__(self, army_id: int, units: list[Unit], general: General):
        self.army_id: int = army_id
        self.units: list[Unit] = units
        self.general: General = general
        
        # S'assure que le général est bien lié à cette armée
        self.general.army_id = army_id

    def __repr__(self) -> str:
        return f"Army({self.army_id}, Général: {self.general.__class__.__name__}, Unités: {len(self.units)})"

    def is_defeated(self) -> bool:
        """
Vérifie si toutes les unités de l'armée sont mortes.
        Utilise une expression de générateur (sec 29.3).
        """
        if not self.units:
            return True # Une armée sans unité est vaincue
            
        # all() est une réduction (sec 24.5.3.4)
        return all(not unit.is_alive for unit in self.units)