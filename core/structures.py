# core/structures.py
from core.unit import Unit, UC_BUILDING, UC_STANDARD_BUILDING, UC_STONE_DEFENSE, UC_UNIQUE_UNIT, DMG_MELEE, DMG_PIERCE
from core.map import Map
from typing import Optional, List

class Building(Unit):
    """
    Base class for buildings.
    """
    def __init__(self, 
                 unit_id: int, 
                 army_id: int, 
                 pos: tuple[float, float],
                 name: str,
                 hp: int, 
                 size: tuple[int, int], # Width, Height in tiles
                 line_of_sight: float,
                 attack_power: int = 0, 
                 attack_range: float = 0.0,
                 reload_time: float = 100.0, # Default slow reload if not attacking
                 armor_melee: int = 1,
                 armor_pierce: int = 8,
                 unit_classes: List[str] = None):
        
        if unit_classes is None:
            unit_classes = [UC_BUILDING, UC_STANDARD_BUILDING]
            
        # Buildings don't move, so speed is 0.
        # Radius = half the smallest dimension (roughly).
        radius = min(size[0], size[1]) / 2.0
        
        super().__init__(
            unit_id=unit_id, 
            army_id=army_id, 
            pos=pos,
            name=name, 
            hp=hp, 
            speed=0.0, 
            line_of_sight=line_of_sight,
            attack_power=attack_power, 
            attack_type=DMG_PIERCE, # Defensive buildings usually shoot arrows
            attack_range=attack_range, 
            reload_time=reload_time,
            armor_melee=armor_melee, 
            armor_pierce=armor_pierce,
            unit_classes=unit_classes,
            radius=radius
        )
        
        self.size = size # (Width, Height) in tiles
        
        # Center position is self.pos. 

    def occupied_tiles(self) -> List[tuple[int, int]]:
        """Returns the list of grid coordinates occupied by this building."""
        # Assume pos is the center. We need to find top-left.
        # Center X = TopLeft X + Width/2
        # TopLeft X = Center X - Width/2
        tl_x = int(self.pos[0] - self.size[0] / 2.0)
        tl_y = int(self.pos[1] - self.size[1] / 2.0)
        
        tiles = []
        for x in range(tl_x, tl_x + self.size[0]):
            for y in range(tl_y, tl_y + self.size[1]):
                tiles.append((x, y))
        return tiles


class Castle(Building):
    """
    Castle: Strong defensive structure. Fires arrows.
    """
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, 
            army_id=army_id, 
            pos=pos,
            name="Castle", 
            hp=4800, 
            size=(4, 4), 
            line_of_sight=11,
            attack_power=11, 
            attack_range=8.0, 
            reload_time=2.0,
            armor_melee=8, 
            armor_pierce=10, # Very resistant to arrows
            unit_classes=[UC_BUILDING, UC_STONE_DEFENSE]
        )

class Wonder(Building):
    """
    Wonder: Victory condition. Massive HP, no attack.
    """
    def __init__(self, unit_id: int, army_id: int, pos: tuple[float, float]):
        super().__init__(
            unit_id=unit_id, 
            army_id=army_id, 
            pos=pos,
            name="Wonder", 
            hp=4800, 
            size=(5, 5), 
            line_of_sight=8,
            attack_power=0, 
            unit_classes=[UC_BUILDING, UC_STANDARD_BUILDING] # Or Unique
        )

# --- Building Placement Helper Functions ---

def is_area_clear(game_map: Map, x: int, y: int, width: int, height: int) -> bool:
    """
    Checks if a rectangular area on the map is free of obstacles and other buildings.
    """
    # Check boundaries
    if x < 0 or y < 0 or x + width > game_map.width or y + height > game_map.height:
        return False
        
    # Check collisions with obstacles
    # Note: Map currently stores obstacles as a list. 
    # For efficiency in a real engine, this should be a grid or spatial hash.
    # We will iterate for now (prototype phase).
    for r in range(x, x + width):
        for c in range(y, y + height):
            for _, ox, oy in game_map.obstacles:
                if int(ox) == r and int(oy) == c:
                    return False
    
    return True

def place_building(game_map: Map, building: Building) -> bool:
    """
    Attempts to place a building on the map.
    """
    # Assume building.pos is currently the intended center.
    tiles = building.occupied_tiles()
    
    # Check if any tile is invalid
    tl_x = int(building.pos[0] - building.size[0] / 2.0)
    tl_y = int(building.pos[1] - building.size[1] / 2.0)
    
    if is_area_clear(game_map, tl_x, tl_y, building.size[0], building.size[1]):
        # Valid placement
        game_map.add_unit(building) # Buildings are Units in our engine
        # Optionally mark tiles as blocked in the map for pathfinding
        return True
    
    return False