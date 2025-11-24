# core/map.py
from core.unit import Unit
from collections import defaultdict

# Utilisation de defaultdict (sec 24.4.1.2) pour simplifier
# la gestion des listes vides.

class Map:
    """
    Gère le monde en coordonnées flottantes (continu)
    et utilise une "matrice creuse" (un dict) pour 
    indexer spatialement les unités (req Prof + Étudiants).
    Ceci est basé sur le concept de l'Exercice 42.
    """
    
    # Taille d'une cellule de la grille de hachage
    CELL_SIZE = 1.0 

    def __init__(self, width: float, height: float):
        self.width: float = width
        self.height: float = height
        
        # La "Matrice Creuse" / Hachage Spatial
        # Fait le lien entre une cellule (int, int) et les unités (float, float)
        # qui s'y trouvent.
        # defaultdict (sec 24.4.1.2) retourne list() si la clé n'existe pas.
        self.spatial_hash: dict[tuple[int, int], list[Unit]] = defaultdict(list)
        
        # Liste pour stocker les obstacles (simples tuples pour l'instant)
        # Format: ("Type", x, y)
        self.obstacles: list[tuple[str, float, float]] = []
        
    def add_obstacle(self, type_name: str, x: float, y: float):
        self.obstacles.append((type_name, x, y))  
    
    def _get_hash_key(self, pos: tuple[float, float]) -> tuple[int, int]:
        """Convertit une position flottante en clé de grille entière."""
        return (int(pos[0] / self.CELL_SIZE), int(pos[1] / self.CELL_SIZE))

    def add_unit(self, unit: Unit):
        """Ajoute une unité à sa position flottante dans la grille."""
        key = self._get_hash_key(unit.pos)
        self.spatial_hash[key].append(unit)

    def remove_unit(self, unit: Unit):
        """Retire une unité de son ancienne position dans la grille."""
        key = self._get_hash_key(unit.pos)
        if unit in self.spatial_hash[key]:
            self.spatial_hash[key].remove(unit)

    def update_unit_position(self, unit: Unit, old_pos: tuple[float, float], new_pos: tuple[float, float]):
        """Met à jour la position d'une unité dans la grille de hachage."""
        old_key = self._get_hash_key(old_pos)
        new_key = self._get_hash_key(new_pos)
        
        unit.pos = new_pos # Mise à jour de la position flottante réelle
        
        if old_key == new_key:
            # L'unité n'a pas changé de cellule de grille, rien à faire.
            return

        # L'unité a changé de cellule, il faut la "déménager"
        if unit in self.spatial_hash[old_key]:
            self.spatial_hash[old_key].remove(unit)
        
        self.spatial_hash[new_key].append(unit)

    def get_units_in_cell(self, cell_key: tuple[int, int]) -> list[Unit]:
        """Retourne les unités dans une cellule de grille donnée."""
        return self.spatial_hash.get(cell_key, [])

    def get_nearby_units(self, unit: Unit, search_radius: float) -> list[Unit]:
        """
        Optimisé ! Trouve les unités proches en ne scannant que
        les cellules de grille adjacentes, pas le monde entier.
        """
        nearby_units = []
        
        # Détermine la plage de cellules de grille à scanner
        radius_in_cells = int(search_radius / self.CELL_SIZE) + 1
        current_cell = self._get_hash_key(unit.pos)
        
        for x in range(current_cell[0] - radius_in_cells, current_cell[0] + radius_in_cells + 1):
            for y in range(current_cell[1] - radius_in_cells, current_cell[1] + radius_in_cells + 1):
                
                for potential_neighbor in self.get_units_in_cell((x, y)):
                    if potential_neighbor == unit:
                        continue
                    
                    # Vérification finale de la distance (Euclidienne)
                    # (car les unités sont en flottant à l'intérieur des cellules)
                    dist = self._calculate_distance(unit.pos, potential_neighbor.pos)
                    if dist <= search_radius:
                        nearby_units.append(potential_neighbor)
                        
        return nearby_units

    @staticmethod
    def _calculate_distance(pos1: tuple[float, float], pos2: tuple[float, float]) -> float:
        """Calcule la distance Euclidienne (proche d'AoE)."""
        # (Nous aurons besoin de 'import math' pour math.sqrt)
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5