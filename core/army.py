# core/army.py
from core.unit import Unit, UC_BUILDING
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
        Vérifie si l'armée est vaincue.
        Une armée est vaincue si elle n'a plus d'unités mobiles (non-bâtiments) en vie.
        (Exclut les bâtiments pour éviter les parties infinies contre des murs/châteaux)
        """
        if not self.units:
            return True # Une armée sans unité est vaincue

        # On cherche s'il reste au moins une unité vivante qui n'est PAS un bâtiment
        has_living_mobile_unit = any(
            unit.is_alive and UC_BUILDING not in unit.armor_classes
            for unit in self.units
        )

        return not has_living_mobile_unit
