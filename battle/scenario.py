from map import SparseMap
from unites import Unit, Knight, Pikeman, Crossbowman
from structures import Building, Wonder, Player, place_wonders_symmetrically, place_building_on_map

class GameMap:
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
    #static grid
        self.static_grid = SparseMap(largeur, hauteur)
    #float positions
        self.units = []
    #buildings
        self.buildings = []
    #players
        self.players = {}
    def add_player(self, player):
        self.players[player.name] = player
        print(f"Player {player.name} joined.")
    def add_unit(self, unit):
        #add unit to map
        self.units.append(unit)
    def add_building(self, building, x_int, y_int):
        #add static buildings
        try:
            place_building_on_map(self.static_grid, building, x_int, y_int)
            self.buildings.append(building)
        except ValueError as e:
            print(f"SCENARIO ERROR: {e}")
    def est_vide(self, x, y):
        return self.static_grid.est_vide(x, y)
    def ajouter(self, x, y, obj):
        self.static_grid.ajouter(x, y, obj)
def create_lanchester_scenario(largeur=120, hauteur=120, num_units=20):
    print("Creating scenario 'Lanchester'...")
    p1 = Player("Player 1 (Blue)")
    p2 = Player("Player 2 (Red)")
    #create map
    game_map = GameMap(largeur, hauteur)
    game_map.add_player(p1)
    game_map.add_player(p2)
    y_wonder = max(0, min(hauteur - 4, hauteur // 2 - 4 // 2))
    try:
        w1, w2 = place_wonders_symmetrically(game_map.static_grid, p1, p2, margin=10)
        game_map.buildings.extend([w1, w2])
        print(f"Placed Wonder of {p1.name} at ({w1.x}, {w1.y})")
        print(f"Placed Wonder of {p2.name} at ({w2.x}, {w2.y})")
    except ValueError as e:
        print(f"CANT PLACE WONDER: {e}")
        return None