# scripts/run_scenario.py
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import math
from core.army import Army
from core.unit import Unit
from ai.generals import MajorDAFT
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
    spacing = 1.5
    
    def get_unit_range(name: str) -> float:
        cls = UNIT_CLASS_MAP.get(name)
        if not cls: return 0.0
        dummy = cls(unit_id=0, army_id=0, pos=(0, 0))
        return dummy.attack_range

    # --- ARMEE 1 (TOP) ---
    army1_units = []
    total_n1 = sum(comp1.values())
    cols1 = int(math.ceil(math.sqrt(total_n1))) if total_n1 > 0 else 1
    rows_count1 = math.ceil(total_n1 / cols1) if total_n1 > 0 else 1
    block_w1 = (cols1 - 1) * spacing
    block_h1 = (rows_count1 - 1) * spacing
    
    half_gap = 40 if height >= 90 else max(5, height // 2 - 10)
    center_x, center_y = width / 2, height / 2
    
    start_x1 = center_x - block_w1 / 2
    start_y1 = center_y - half_gap - block_h1 # Top row of the block
    
    # Sort: Higher range units first (row 0 is the "back" for Army 1)
    sorted_types1 = sorted(comp1.keys(), key=get_unit_range, reverse=True)
    
    current_idx = 0
    for unit_name in sorted_types1:
        count = comp1[unit_name]
        u_class = UNIT_CLASS_MAP[unit_name]
        for _ in range(count):
            row, col = divmod(current_idx, cols1)
            pos_x = start_x1 + col * spacing
            pos_y = start_y1 + row * spacing # row 0 = furthest from center
            
            unit = u_class(unit_id=current_idx, army_id=0, pos=(pos_x, pos_y))
            army1_units.append(unit)
            current_idx += 1

    # --- ARMEE 2 (BOTTOM) ---
    army2_units = []
    total_n2 = sum(comp2.values())
    cols2 = int(math.ceil(math.sqrt(total_n2))) if total_n2 > 0 else 1
    rows_count2 = math.ceil(total_n2 / cols2) if total_n2 > 0 else 1
    block_w2 = (cols2 - 1) * spacing
    block_h2 = (rows_count2 - 1) * spacing
    
    start_x2 = center_x + block_w2 / 2
    start_y2 = center_y + half_gap + block_h2 # Bottom row of the block

    # Sort: Higher range units first (row 0 is the "back" for Army 2)
    sorted_types2 = sorted(comp2.keys(), key=get_unit_range, reverse=True)

    current_idx_2 = 0
    for unit_name in sorted_types2:
        count = comp2[unit_name]
        u_class = UNIT_CLASS_MAP[unit_name]
        for _ in range(count):
            row, col = divmod(current_idx_2, cols2)
            pos_x = start_x2 - col * spacing
            pos_y = start_y2 - row * spacing # row 0 = furthest from center
            
            unit = u_class(unit_id=10000 + current_idx_2, army_id=1, pos=(pos_x, pos_y))
            army2_units.append(unit)
            current_idx_2 += 1

    army1 = Army(army_id=0, units=army1_units, general=general_class1(army_id=0))
    army2 = Army(army_id=1, units=army2_units, general=general_class2(army_id=1))

    return army1, army2
