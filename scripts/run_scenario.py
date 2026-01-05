# scenarios.py
import sys
import os

# Add project root to path
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
    
    army1_units = []
    # Calcul du nombre de colonnes/lignes pour le bloc (carré approximatif)
    total_n1 = sum(comp1.values())
    cols1 = int(math.ceil(math.sqrt(total_n1))) if total_n1 > 0 else 1
    rows_count1 = math.ceil(total_n1 / cols1) if total_n1 > 0 else 1
    
    spacing = 1.5
    
    # Dimensions graphiques du bloc d'armée 1
    block_w1 = (cols1 - 1) * spacing
    block_h1 = (rows_count1 - 1) * spacing
    
    # GAP de 80 demandé => 40 de chaque côté du centre
    # Adaptation si la map est trop petite (< 100 de haut)
    half_gap = 40
    if height < 90:
        half_gap = max(5, height // 2 - 10) # Marge minime
        
    center_x = width / 2
    center_y = height / 2
    
    # P1 (Haut) : Doit FINIR à (center_y - half_gap)
    # Remplissage par pos_y = start_y1 + row*spacing
    # Donc start_y1 + block_h1 = center_y - half_gap
    # => start_y1 = center_y - half_gap - block_h1
    
    # Centrage X : commence à start_x1 + col*spacing
    # start_x1 + block_w1/2 = center_x
    # => start_x1 = center_x - block_w1 / 2
    
    start_x1 = center_x - block_w1 / 2
    start_y1 = center_y - half_gap - block_h1
    
    current_idx = 0
    for unit_name, count in comp1.items():
        if count <= 0: continue
        
        u_class = UNIT_CLASS_MAP[unit_name]
        
        for _ in range(count):
            row = current_idx // cols1
            col = current_idx % cols1
            
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
    cols2 = int(math.ceil(math.sqrt(total_n2))) if total_n2 > 0 else 1
    rows_count2 = math.ceil(total_n2 / cols2) if total_n2 > 0 else 1
    
    block_w2 = (cols2 - 1) * spacing
    block_h2 = (rows_count2 - 1) * spacing
    
    # P2 (Bas) : Doit COMMENCER à (center_y + half_gap)
    # Remplissage par pos_y = start_y2 - row*spacing (décroissant, vers le haut ?)
    # ATTENTION : La logique précédente (user edit) était start_y2 - row*spacing.
    # Si on garde ce sens (0 = ligne du bas), alors le sommet du bloc est (start_y2 - block_h2).
    # On veut que le SOMMET soit à center_y + half_gap.
    # => start_y2 - block_h2 = center_y + half_gap
    # => start_y2 = center_y + half_gap + block_h2
    
    # Centrage X : P2 remplit par start_x2 - col*spacing (vers la gauche)
    # Donc start_x2 est le bord DROIT.
    # Centre = start_x2 - block_w2 / 2
    # => start_x2 = center_x + block_w2 / 2
    
    start_x2 = center_x + block_w2 / 2
    start_y2 = center_y + half_gap + block_h2

    current_idx_2 = 0
    for unit_name, count in comp2.items():
        if count <= 0: continue
        
        u_class = UNIT_CLASS_MAP[unit_name]
        
        for _ in range(count):
            row = current_idx_2 // cols2
            col = current_idx_2 % cols2
            
            # Pour P2, on décrémente pour aller vers l'intérieur de la map
            pos_x = start_x2 - col * spacing
            pos_y = start_y2 - row * spacing
            
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