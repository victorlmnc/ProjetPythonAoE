# view/terminal_view.py
import os
import time
from core.map import Map
from core.unit import Unit, Knight, Pikeman, Archer
from core.army import Army

class TerminalView:
    """
    Gère l'affichage ASCII dans le terminal (Req 9.a).
    Utilise des codes ANSI pour les couleurs.
    """
    
    # Codes couleurs ANSI
    BLUE = '\033[94m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    GREY = '\033[90m'
    RESET = '\033[0m'
    
    # Symboles
    SYMBOL_EMPTY = '.'
    SYMBOL_TREE = '♣'
    SYMBOL_ROCK = '▲'
    
    def __init__(self, map_instance: Map):
        self.map = map_instance
        self.width = int(map_instance.width)
        self.height = int(map_instance.height)

    def display(self, armies: list[Army], turn: int):
        """
        Génère et affiche la frame courante.
        """
        # 1. Nettoyer l'écran (Cross-platform)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"--- TOUR {turn} ---")
        
        # 2. Créer une grille vide (buffer)
        # Attention: grid[y][x] car on imprime ligne par ligne
        grid = [[self.SYMBOL_EMPTY for _ in range(self.width)] for _ in range(self.height)]
        
        # 3. Placer les obstacles (Statiques)
        for type_name, x, y in self.map.obstacles:
            ix, iy = int(x), int(y)
            if 0 <= ix < self.width and 0 <= iy < self.height:
                if type_name == "Tree":
                    grid[iy][ix] = f"{self.GREEN}{self.SYMBOL_TREE}{self.RESET}"
                elif type_name == "Rock":
                    grid[iy][ix] = f"{self.GREY}{self.SYMBOL_ROCK}{self.RESET}"

        # 4. Placer les unités (Dynamiques)
        # On itère sur toutes les armées
        for army in armies:
            color = self.BLUE if army.army_id == 0 else self.RED
            
            for unit in army.units:
                if not unit.is_alive:
                    continue
                
                # Conversion Flottant -> Grille Entière
                ix = int(unit.pos[0])
                iy = int(unit.pos[1])
                
                # Vérification des limites (sécurité)
                if 0 <= ix < self.width and 0 <= iy < self.height:
                    symbol = self._get_unit_symbol(unit)
                    # On place le caractère coloré dans la grille
                    grid[iy][ix] = f"{color}{symbol}{self.RESET}"

        # 5. Rendu final (Rasterization)
        # On joint tout en une seule grande chaîne pour éviter le scintillement
        output_lines = []
        # Bordure supérieure
        output_lines.append("+" + "-" * self.width + "+")
        
        for row in grid:
            output_lines.append("|" + "".join(row) + "|")
            
        # Bordure inférieure
        output_lines.append("+" + "-" * self.width + "+")
        
        # Affichage des stats rapides
        stats = f"Armée 0 (Bleu): {self._count_alive(armies[0])} vivants | "
        stats += f"Armée 1 (Rouge): {self._count_alive(armies[1])} vivants"
        output_lines.append(stats)
        
        print("\n".join(output_lines))
        
        # Petite pause pour que l'œil humain puisse suivre (0.1s à 0.5s)
        time.sleep(0.2)

    def _get_unit_symbol(self, unit: Unit) -> str:
        """Retourne une lettre selon le type d'unité."""
        if isinstance(unit, Knight): return 'K'
        if isinstance(unit, Pikeman): return 'P'
        if isinstance(unit, Archer): return 'A'
        return '?'

    def _count_alive(self, army: Army) -> int:
        return sum(1 for u in army.units if u.is_alive)