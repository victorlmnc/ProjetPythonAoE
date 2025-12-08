# scenarios.py
import math
from core.army import Army
from core.unit import Unit
from ai.generals_impl_IA import MajorDAFT
from core.definitions import GENERAL_CLASS_MAP, UNIT_CLASS_MAP

def lanchester_scenario(unit_class: type[Unit], n: int, general_class=MajorDAFT):
    """
    Creates a scenario for testing Lanchester's Laws.
    """
    comp1 = {unit_class.__name__: n}
    comp2 = {unit_class.__name__: 2*n}
    
    return custom_battle_scenario(
        comp1, comp2, 
        general_class, general_class, 
        (40, 40)
    )

def custom_battle_scenario(comp1: dict[str, int], 
                           comp2: dict[str, int],
                           general_class1: type, 
                           general_class2: type,
                           map_size: tuple[int, int] = (120, 120)):
    
    width, height = map_size
    
    army1_units = []
    total_n1 = sum(comp1.values())
    rows1 = int(math.ceil(math.sqrt(total_n1))) if total_n1 > 0 else 1
    spacing = 1.5
    start_x1 = 10.0
    start_y1 = 10.0
    
    current_idx = 0
    for unit_name, count in comp1.items():
        if count <= 0: continue
        
        u_class = UNIT_CLASS_MAP[unit_name]
        
        for _ in range(count):
            row = current_idx // rows1
            col = current_idx % rows1
            
            pos_x = start_x1 + col * spacing
            pos_y = start_y1 + row * spacing
            
            # Clamp
            pos_x = min(width-2, max(1, pos_x))
            pos_y = min(height-2, max(1, pos_y))
            
            unit = u_class(unit_id=current_idx, army_id=0, pos=(pos_x, pos_y))
            army1_units.append(unit)
            current_idx += 1

    army2_units = []
    total_n2 = sum(comp2.values())
    rows2 = int(math.ceil(math.sqrt(total_n2))) if total_n2 > 0 else 1
    start_x2 = 10.0
    start_y2 = height - 15.0 - (rows2 * spacing)
    if start_y2 < start_y1 + (rows1 * spacing) + 5:
        start_y2 = max(height//2 + 5, start_y2)

    current_idx_2 = 0
    for unit_name, count in comp2.items():
        if count <= 0: continue
        
        u_class = UNIT_CLASS_MAP[unit_name]
        
        for _ in range(count):
            row = current_idx_2 // rows2
            col = current_idx_2 % rows2
            
            pos_x = start_x2 + col * spacing
            pos_y = start_y2 + row * spacing
            
            # Clamp
            pos_x = min(width-2, max(1, pos_x))
            pos_y = min(height-2, max(1, pos_y))
            
            # ID offset 10000 to avoid collision
            unit = u_class(unit_id=10000 + current_idx_2, army_id=1, pos=(pos_x, pos_y))
            army2_units.append(unit)
            current_idx_2 += 1

    army1 = Army(army_id=0, units=army1_units, general=general_class1(army_id=0))
    army2 = Army(army_id=1, units=army2_units, general=general_class2(army_id=1))

    return army1, army2