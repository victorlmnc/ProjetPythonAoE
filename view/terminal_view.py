# view/terminal_view.py
import os
import sys
import time
from datetime import datetime
from core.map import Map
from core.unit import Unit, Knight, Pikeman, Crossbowman, LongSwordsman, EliteSkirmisher, CavalryArcher, Onager
from core.army import Army

# Import conditionnel pour la capture clavier selon l'OS
if os.name == 'nt':
    import msvcrt
else:
    import select
    import tty
    import termios

class TerminalView:
    """
    Gère l'affichage ASCII dans le terminal (Req 9.a).
    Utilise des codes ANSI pour les couleurs.
    Supporte les raccourcis clavier P (Pause), TAB (Snapshot HTML).
    """
    
    # Codes couleurs ANSI
    BLUE = '\033[94m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    GREY = '\033[90m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    
    # Symboles
    SYMBOL_EMPTY = '.'
    SYMBOL_TREE = '♣'
    SYMBOL_ROCK = '▲'
    
    def __init__(self, map_instance: Map):
        self.map = map_instance
        self.width = int(map_instance.width)
        self.height = int(map_instance.height)
        # Limiter l'affichage pour les grandes cartes
        self.max_display_width = min(80, self.width)
        self.max_display_height = min(40, self.height)
        # Offset pour le scroll (ZQSD)
        self.scroll_x = 0
        self.scroll_y = 0
        
    def _check_keyboard(self) -> str | None:
        """
        Vérifie si une touche a été pressée (non-bloquant).
        Retourne le caractère pressé ou None.
        """
        if os.name == 'nt':
            # Windows
            if msvcrt.kbhit():
                key = msvcrt.getch()
                # Gestion des touches spéciales (F9, F11, F12)
                if key == b'\x00' or key == b'\xe0':
                    special = msvcrt.getch()
                    if special == b'C':  # F9
                        return 'F9'
                    elif special == b'\x85':  # F11
                        return 'F11'
                    elif special == b'\x86':  # F12
                        return 'F12'
                return key.decode('utf-8', errors='ignore').lower()
        else:
            # Linux/Mac
            if select.select([sys.stdin], [], [], 0)[0]:
                return sys.stdin.read(1).lower()
        return None

    def display(self, armies: list[Army], turn: int, paused: bool = False) -> str | None:
        """
        Génère et affiche la frame courante.
        Retourne une commande si une touche spéciale est pressée.
        """
        # 1. Vérifier les entrées clavier
        key = self._check_keyboard()
        command = None
        
        if key == 'p':
            command = "toggle_pause"
        elif key == '\t' or key == 'tab':
            # Générer un snapshot HTML instantané
            self._generate_html_snapshot(armies, turn)
            print(f"{self.YELLOW}>>> Snapshot HTML généré !{self.RESET}")
        elif key == 'q':
            command = "quit"
        elif key == 'z':
            self.scroll_y = max(0, self.scroll_y - 5)
        elif key == 's':
            self.scroll_y = min(self.height - self.max_display_height, self.scroll_y + 5)
        elif key == 'd':
            self.scroll_x = min(self.width - self.max_display_width, self.scroll_x + 5)
        elif key == 'F9':
            command = "switch_view"
        elif key == 'F11':
            command = "quick_save"
        elif key == 'F12':
            command = "quick_load"
        
        # 2. Nettoyer l'écran (Cross-platform)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 3. Afficher le header
        status = f"{self.RED}[PAUSE]{self.RESET}" if paused else f"{self.GREEN}[EN COURS]{self.RESET}"
        print(f"--- TOUR {turn} --- {status}")
        print(f"Contrôles: [P] Pause | [TAB] Snapshot HTML | [ZQSD] Scroll | [Q] Quitter")
        print(f"Scroll: ({self.scroll_x}, {self.scroll_y})\n")
        
        # 4. Créer une grille vide (buffer)
        # On affiche seulement la portion visible
        visible_width = min(self.max_display_width, self.width - self.scroll_x)
        visible_height = min(self.max_display_height, self.height - self.scroll_y)
        
        grid = [[self.SYMBOL_EMPTY for _ in range(visible_width)] for _ in range(visible_height)]
        
        # 5. Placer les obstacles (Statiques)
        for type_name, x, y in self.map.obstacles:
            ix, iy = int(x) - self.scroll_x, int(y) - self.scroll_y
            if 0 <= ix < visible_width and 0 <= iy < visible_height:
                if type_name == "Tree":
                    grid[iy][ix] = f"{self.GREEN}{self.SYMBOL_TREE}{self.RESET}"
                elif type_name == "Rock":
                    grid[iy][ix] = f"{self.GREY}{self.SYMBOL_ROCK}{self.RESET}"

        # 6. Placer les unités (Dynamiques)
        for army in armies:
            color = self.BLUE if army.army_id == 0 else self.RED
            
            for unit in army.units:
                if not unit.is_alive:
                    continue
                
                # Conversion Flottant -> Grille Entière avec scroll
                ix = int(unit.pos[0]) - self.scroll_x
                iy = int(unit.pos[1]) - self.scroll_y
                
                if 0 <= ix < visible_width and 0 <= iy < visible_height:
                    symbol = self._get_unit_symbol(unit)
                    grid[iy][ix] = f"{color}{symbol}{self.RESET}"

        # 7. Rendu final (Rasterization)
        output_lines = []
        output_lines.append("+" + "-" * visible_width + "+")
        
        for row in grid:
            output_lines.append("|" + "".join(row) + "|")
            
        output_lines.append("+" + "-" * visible_width + "+")
        
        # Affichage des stats rapides
        stats = f"Armée 0 (Bleu): {self._count_alive(armies[0])} vivants | "
        stats += f"Armée 1 (Rouge): {self._count_alive(armies[1])} vivants"
        output_lines.append(stats)
        
        print("\n".join(output_lines))
        
        # Petite pause pour que l'œil humain puisse suivre
        time.sleep(0.1)
        
        return command

    def _generate_html_snapshot(self, armies: list[Army], turn: int):
        """
        Génère un fichier HTML instantané listant toutes les unités et leurs stats.
        Requis par le PDF (touche TAB).
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"saves/snapshot_turn{turn}_{timestamp}.html"
        
        # Créer le dossier saves si nécessaire
        os.makedirs("saves", exist_ok=True)
        
        html = [
            "<!DOCTYPE html>",
            "<html><head><meta charset='UTF-8'>",
            f"<title>MedievAIl - Snapshot Tour {turn}</title>",
            "<style>",
            "body { font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }",
            "h1 { color: #e94560; }",
            "table { border-collapse: collapse; width: 100%; margin: 20px 0; }",
            "th, td { border: 1px solid #444; padding: 8px; text-align: left; }",
            "th { background: #16213e; }",
            ".blue { color: #4d9de0; }",
            ".red { color: #e94560; }",
            ".dead { color: #666; text-decoration: line-through; }",
            "</style>",
            "</head><body>",
            f"<h1>🏰 MedievAIl - Snapshot Tour {turn}</h1>",
            f"<p>Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
        ]
        
        for i, army in enumerate(armies):
            color_class = "blue" if i == 0 else "red"
            alive_count = self._count_alive(army)
            total_count = len(army.units)
            
            html.append(f"<h2 class='{color_class}'>Armée {i} - {army.general.__class__.__name__}</h2>")
            html.append(f"<p>Unités: {alive_count}/{total_count} en vie</p>")
            html.append("<table>")
            html.append("<tr><th>Type</th><th>ID</th><th>HP</th><th>Position</th><th>Attaque</th><th>Armure</th><th>Statut</th></tr>")
            
            for unit in army.units:
                status_class = "" if unit.is_alive else "dead"
                status_text = "En vie" if unit.is_alive else "Mort"
                armor_text = f"M:{unit.melee_armor} / P:{unit.pierce_armor}"
                
                html.append(f"<tr class='{status_class}'>")
                html.append(f"<td>{unit.__class__.__name__}</td>")
                html.append(f"<td>{unit.unit_id}</td>")
                html.append(f"<td>{unit.current_hp}/{unit.max_hp}</td>")
                html.append(f"<td>({unit.pos[0]:.1f}, {unit.pos[1]:.1f})</td>")
                html.append(f"<td>{unit.attack_power} ({unit.attack_type})</td>")
                html.append(f"<td>{armor_text}</td>")
                html.append(f"<td>{status_text}</td>")
                html.append("</tr>")
            
            html.append("</table>")
        
        html.append("</body></html>")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(html))
        
        print(f"Snapshot sauvegardé: {os.path.abspath(filename)}")

    def _get_unit_symbol(self, unit: Unit) -> str:
        """Retourne une lettre selon le type d'unité."""
        if isinstance(unit, Knight): return 'K'
        if isinstance(unit, Pikeman): return 'P'
        if isinstance(unit, Crossbowman): return 'C'
        if isinstance(unit, LongSwordsman): return 'L'
        if isinstance(unit, EliteSkirmisher): return 'E'
        if isinstance(unit, CavalryArcher): return 'A'
        if isinstance(unit, Onager): return 'O'
        return '?'

    def _count_alive(self, army: Army) -> int:
        return sum(1 for u in army.units if u.is_alive)