import pygame
import os
from core.map import Map
from core.army import Army

# --- CONSTANTES DE CONFIGURATION VUE ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BG_COLOR = (30, 30, 30)

# Dimensions isométriques (Ratio 2:1)
TILE_WIDTH = 64
TILE_HEIGHT = 32
TILE_HALF_W = TILE_WIDTH // 2
TILE_HALF_H = TILE_HEIGHT // 2

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
BLUE = (50, 50, 200)
GREEN = (50, 200, 50)

# Couleurs Terrain
TERRAIN_COLORS = {
    0: (100, 200, 100),  # Herbe basse
    1: (120, 180, 100),  # Herbe
    2: (140, 160, 80),   # Terre
    3: (160, 140, 60),   # Colline
    4: (180, 120, 40),   # Montagne
}
WATER_COLOR = (60, 100, 200)
OBSTACLE_COLOR = (100, 100, 100) # Gris pour les obstacles

MINIMAP_SIZE = 200
MINIMAP_MARGIN = 20

class PygameView:
    def __init__(self, game_map: Map):
        pygame.init()
        pygame.display.set_caption("MedievAIl - Isometric View")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.map = game_map
        self.font = pygame.font.SysFont('Arial', 16, bold=True)
        self.ui_font = pygame.font.SysFont('Arial', 24, bold=True)

        # --- Assets ---
        self.textures = {}
        self.load_assets()

        # --- Caméra ---
        self.scroll_x = 0
        self.scroll_y = 0
        self.scroll_speed = 15

        # Centrage initial
        center_map_x = self.map.width / 2
        center_map_y = self.map.height / 2
        iso_center_x = (center_map_x - center_map_y) * TILE_HALF_W
        iso_center_y = (center_map_x + center_map_y) * TILE_HALF_H
        self.offset_x = SCREEN_WIDTH / 2 - iso_center_x
        self.offset_y = SCREEN_HEIGHT / 2 - iso_center_y

    def load_assets(self):
        """Loads graphical assets from the assets directory."""
        # Mapping: Unit Class Name -> File Path
        mapping = {
            "Knight": "assets/units/knight/walk/hosreman_walk.webp", # Typo in filename 'hosreman'
            "Crossbowman": "assets/units/crossbowman/walk/crossbowman_walk.webp",
            "LongSwordsman": "assets/units/longswordman/walk/swordsman_walk.webp",
            "Archer": "assets/units/archer/walk/archer_walk.webp"
        }

        # Fallbacks for other unit types
        mapping["Pikeman"] = mapping["LongSwordsman"]
        mapping["EliteSkirmisher"] = mapping["Archer"]
        mapping["CavalryArcher"] = mapping["Archer"]

        for class_name, path in mapping.items():
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path)
                    # Scale down since original sprites might be large
                    # Adjust size as needed. Let's try 48x48 centered.
                    img = pygame.transform.scale(img, (48, 48))
                    self.textures[class_name] = img
                    print(f"Loaded asset for {class_name}: {path}")
                except Exception as e:
                    print(f"Failed to load asset for {class_name} at {path}: {e}")
            else:
                # Only warn if it was an explicit path, not a fallback logic that might fail silently
                pass

    def cart_to_iso(self, x: float, y: float) -> tuple[int, int]:
        """
        Convertit les coordonnées cartésiennes (grille) en coordonnées d'écran isométriques.

        Maths:
        - On effectue une rotation de 45 degrés et un écrasement vertical (projection dimétrique 2:1).
        - x_iso = (x_cart - y_cart) * largeur_tuile / 2
        - y_iso = (x_cart + y_cart) * hauteur_tuile / 2

        On ajoute ensuite les offsets de centrage et de défilement caméra.
        """
        iso_x = (x - y) * TILE_HALF_W
        iso_y = (x + y) * TILE_HALF_H
        final_x = iso_x + self.offset_x - self.scroll_x
        final_y = iso_y + self.offset_y - self.scroll_y
        return int(final_x), int(final_y)

    def check_events(self) -> str | None:
        """Gère clavier/souris."""
        keys = pygame.key.get_pressed()

        # Déplacement Caméra
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.scroll_x -= self.scroll_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.scroll_x += self.scroll_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: self.scroll_y -= self.scroll_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s] and not (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
            self.scroll_y += self.scroll_speed

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return "quit"
                if event.key == pygame.K_SPACE: return "toggle_pause"
                if event.key == pygame.K_s: return "step"
        return None

    def draw_map(self):
        """Dessine le sol et les obstacles."""

        obstacles_dict = {(int(x), int(y)): type_name for type_name, x, y in self.map.obstacles}

        for y in range(self.map.height):
            for x in range(self.map.width):
                # CORRECTION 1 : grid[x][y] et non [y][x]
                tile = self.map.grid[x][y]

                screen_x, screen_y = self.cart_to_iso(x, y)

                # Optimisation : ne pas dessiner hors écran
                if not (-200 < screen_x < SCREEN_WIDTH + 200 and -200 < screen_y < SCREEN_HEIGHT + 200):
                   continue

                # Couleur Terrain
                if tile.terrain_type == 'water':
                    color = WATER_COLOR
                    height_offset = 0
                else:
                    elev_idx = min(int(tile.elevation / 4), 4)
                    color = TERRAIN_COLORS.get(elev_idx, TERRAIN_COLORS[0])
                    height_offset = int(tile.elevation) * 2

                # Obstacles
                if (x, y) in obstacles_dict:
                    color = OBSTACLE_COLOR
                    height_offset += 15

                # Dessin du losange
                base_y = screen_y - height_offset
                points = [
                    (screen_x, base_y - TILE_HALF_H),
                    (screen_x + TILE_HALF_W, base_y),
                    (screen_x, base_y + TILE_HALF_H),
                    (screen_x - TILE_HALF_W, base_y)
                ]
                pygame.draw.polygon(self.screen, color, points)

                # Effet 3D
                if height_offset > 0 and tile.terrain_type != 'water':
                     darker = (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40))
                     pygame.draw.polygon(self.screen, darker, [
                         (screen_x - TILE_HALF_W, base_y),
                         (screen_x, base_y + TILE_HALF_H),
                         (screen_x, screen_y + TILE_HALF_H),
                         (screen_x - TILE_HALF_W, screen_y)
                     ])
                     medium = (max(0, color[0]-20), max(0, color[1]-20), max(0, color[2]-20))
                     pygame.draw.polygon(self.screen, medium, [
                         (screen_x + TILE_HALF_W, base_y),
                         (screen_x, base_y + TILE_HALF_H),
                         (screen_x, screen_y + TILE_HALF_H),
                         (screen_x + TILE_HALF_W, screen_y)
                     ])

    def draw_units(self, armies: list[Army]):
        """Dessine les unités."""
        all_units = []
        for army in armies:
            for unit in army.units:
                if unit.is_alive:
                    all_units.append((army.army_id, unit))

        all_units.sort(key=lambda p: (round(p[1].pos[1]), round(p[1].pos[0])))

        for army_id, unit in all_units:
            x, y = unit.pos
            ix, iy = int(x), int(y)

            # CORRECTION 2 : Vérification limites + grid[ix][iy]
            if 0 <= ix < self.map.width and 0 <= iy < self.map.height:
                tile = self.map.grid[ix][iy]
            else:
                continue # Ignore l'unité si elle est hors carte

            height_offset = 0
            if tile.terrain_type != 'water':
                 height_offset = int(tile.elevation) * 2

            screen_x, screen_y = self.cart_to_iso(x, y)
            unit_draw_y = screen_y - height_offset

            unit_class_name = unit.__class__.__name__

            if unit_class_name in self.textures:
                img = self.textures[unit_class_name]
                # Center the image
                rect = img.get_rect(center=(screen_x, unit_draw_y - 16))
                self.screen.blit(img, rect)

                # Health bar
                hp_ratio = unit.current_hp / unit.max_hp
                pygame.draw.rect(self.screen, RED, (screen_x - 10, unit_draw_y - 45, 20, 3))
                pygame.draw.rect(self.screen, GREEN, (screen_x - 10, unit_draw_y - 45, 20 * hp_ratio, 3))

                # Army indicator (small circle)
                color = BLUE if army_id == 0 else RED
                pygame.draw.circle(self.screen, color, (screen_x + 10, unit_draw_y - 5), 4)

            else:
                # Fallback to circle
                color = BLUE if army_id == 0 else RED
                pygame.draw.circle(self.screen, color, (screen_x, unit_draw_y - 10), 6)

                hp_ratio = unit.current_hp / unit.max_hp
                pygame.draw.rect(self.screen, RED, (screen_x - 10, unit_draw_y - 25, 20, 3))
                pygame.draw.rect(self.screen, GREEN, (screen_x - 10, unit_draw_y - 25, 20 * hp_ratio, 3))

    def draw_ui(self, turn_count, paused, armies):
        """Interface Utilisateur."""
        if paused:
            txt = self.ui_font.render("PAUSE (Espace pour reprendre)", True, WHITE, RED)
            self.screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 20))

        turn_txt = self.ui_font.render(f"Tour: {turn_count}", True, WHITE)
        self.screen.blit(turn_txt, (20, 20))

        y = 60
        for i, army in enumerate(armies):
             alive = sum(1 for u in army.units if u.is_alive)
             txt = self.font.render(f"Armée {i}: {alive} unités", True, BLUE if i==0 else RED)
             self.screen.blit(txt, (20, y))
             y += 25

        # Minimap
        mm_x, mm_y = SCREEN_WIDTH - MINIMAP_SIZE - 20, SCREEN_HEIGHT - MINIMAP_SIZE - 20
        pygame.draw.rect(self.screen, BLACK, (mm_x, mm_y, MINIMAP_SIZE, MINIMAP_SIZE))

        scale_x = MINIMAP_SIZE / self.map.width
        scale_y = MINIMAP_SIZE / self.map.height

        for _, ox, oy in self.map.obstacles:
            pygame.draw.rect(self.screen, (100,100,100), (mm_x + ox*scale_x, mm_y + oy*scale_y, 2, 2))

        for army in armies:
            c = BLUE if army.army_id == 0 else RED
            for u in army.units:
                if u.is_alive:
                    pygame.draw.circle(self.screen, c, (mm_x + int(u.pos[0]*scale_x), mm_y + int(u.pos[1]*scale_y)), 2)

    def display(self, armies: list[Army], turn_count: int, paused: bool) -> str | None:
        cmd = self.check_events()
        self.screen.fill(BG_COLOR)
        self.draw_map()
        self.draw_units(armies)
        self.draw_ui(turn_count, paused, armies)
        pygame.display.flip()
        self.clock.tick(60)
        return cmd