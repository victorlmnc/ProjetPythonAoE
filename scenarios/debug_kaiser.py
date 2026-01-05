
from core.unit import Knight, Crossbowman
from core.map import Map
from core.army import Army
from ai.generals import MajorDAFT, ColonelKAISER

def create_scenario(class1, class2):
    # 1. Création de la Carte
    game_map = Map(40, 40)
    
    # 2. Création des Armées
    # Army 1 (ColonelKAISER): Mixed composition
    units1 = []
    # 5 Knights (Melee)
    for i in range(5):
        units1.append(Knight(i, 0, (5.0, 5.0 + i)))
    # 5 Crossbowmen (Ranged)
    for i in range(5):
        units1.append(Crossbowman(100+i, 0, (2.0, 5.0 + i)))
        
    army1 = Army(0, units1, ColonelKAISER(0))
    
    # Army 2 (MajorDAFT): Just Knights
    units2 = []
    for i in range(10):
        units2.append(Knight(200+i, 1, (35.0, 5.0 + i)))
        
    army2 = Army(1, units2, MajorDAFT(1))
    
    return army1, army2, game_map
