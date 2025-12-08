import pygame
import os
from io import BytesIO
from PIL import Image

from core.map import Map
from core.army import Army
# Import de toutes les classes d'unités pour le mappage des sprites
from core.unit import Knight, Pikeman, Crossbowman, LongSwordsman

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

# Taille d'une seule frame dans VOS spritesheets (estimée).
SPRITE_FRAME_WIDTH = 48  
SPRITE_FRAME_HEIGHT = 72 

class PygameView:
    def __init__(self, game_map: Map):
        pygame.init()
        pygame.display.set_caption("MedievAIl - Isometric View")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.map = game_map
        self.font = pygame.font.SysFont('Arial', 16, bold=True)
        self.ui_font = pygame.font.SysFont('Arial', 24, bold=True)

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
        
        # --- LIGNES DE DÉBOGAGE POUR LES ARBRES ---
        # Ajout de plusieurs arbres à des positions fixes pour test
        self.map.add_obstacle("Tree", 10, 10) 
        self.map.add_obstacle("Tree", 15, 5)  
        self.map.add_obstacle("Tree", 5, 15)  
        self.map.add_obstacle("Tree", 20, 15) 
        # ----------------------------------------

        # --- Sprites (Assets unifiés) ---
        self.unit_sprites: dict = {}
        self.tree_sprite: pygame.Surface | None = None
        self.grass_sprite: pygame.Surface | None = None
        self._load_sprites()
        print("Chargement des assets de fond terminé.")


    def _load_webp_asset(self, path: str, target_size: tuple[int, int], is_spritesheet: bool) -> pygame.Surface | None:
        """
        Charge un fichier WEBP via Pillow, le convertit en PNG in-memory,
        le charge dans Pygame, et le met à l'échelle.
        """
        try:
            pil_img = Image.open(path)
            
            if is_spritesheet:
                # Découpe la première frame (position 0,0)
                frame_area = (0, 0, SPRITE_FRAME_WIDTH, SPRITE_FRAME_HEIGHT)
                pil_img = pil_img.crop(frame_area)
            
            # Conversion Pillow -> BytesIO -> Pygame Surface
            data = BytesIO()
            pil_img.save(data, format='PNG')
            data.seek(0)
            
            surface = pygame.image.load(data, 'PNG').convert_alpha()

            # Mise à l'échelle (pour l'affichage isométrique)
            return pygame.transform.scale(surface, target_size)

        except FileNotFoundError:
            print(f"Erreur FATALE: Fichier non trouvé: {path}")
            return None
        except Exception as e:
            print(f"Erreur de chargement de l'asset {path}: {e}")
            return None

    def _load_sprites(self):
        """
        Charge tous les assets graphiques nécessaires.
        """
        BASE_PATH = "assets" 
        
        # --- Ressources (Gazon et Arbre) ---
        grass_path = os.path.join(BASE_PATH, "resources/grass/grass.webp")
        self.grass_sprite = self._load_webp_asset(grass_path, target_size=(TILE_WIDTH, TILE_WIDTH // 2 + 16), is_spritesheet=False) 

        tree_path = os.path.join(BASE_PATH, "resources/tree/Tree.webp")
        self.tree_sprite = self._load_webp_asset(tree_path, target_size=(60, 90), is_spritesheet=False) 
        
        # --- Unités ---
        unit_configs = {
            Knight: (os.path.join(BASE_PATH, "units/knight/walk/hosreman_walk.webp"), (SPRITE_FRAME_WIDTH * 1.5, SPRITE_FRAME_HEIGHT * 1.5)),
            Crossbowman: (os.path.join(BASE_PATH, "units/crossbowman/walk/crossbowman_walk.webp"), (SPRITE_FRAME_WIDTH * 1.5, SPRITE_FRAME_HEIGHT * 1.5)),
            Pikeman: (os.path.join(BASE_PATH, "units/longswordman/walk/swordsman_walk.webp"), (SPRITE_FRAME_WIDTH * 1.5, SPRITE_FRAME_HEIGHT * 1.5)),
            LongSwordsman: (os.path.join(BASE_PATH, "units/longswordman/walk/swordsman_walk.webp"), (SPRITE_FRAME_WIDTH * 1.5, SPRITE_FRAME_HEIGHT * 1.5)),
        }
        
        for unit_class, (path, size) in unit_configs.items():
            self.unit_sprites[unit_class] = self._load_webp_asset(path, size, is_spritesheet=True)


    def cart_to_iso(self, x: float, y: float) -> tuple[int, int]:
        """Convertit grille -> isométrique."""
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
                tile = self.map.grid[x][y]
                
                screen_x, screen_y = self.cart_to_iso(x, y)
                
                # Optimisation : ne pas dessiner hors écran
                if not (-100 < screen_x < SCREEN_WIDTH + 100 and -100 < screen_y < SCREEN_HEIGHT + 100):
                   continue

                # 1. Calcul de l'élévation et de la position d'ancrage Y
                height_offset = 0
                if tile.terrain_type != 'water':
                    height_offset = int(tile.elevation) * 2
                    
                base_y = screen_y - height_offset

                # 2. DESSIN DU FOND (GAZON ou COULEUR)
                if self.grass_sprite and tile.terrain_type != 'water' and tile.elevation == 0:
                    sprite = self.grass_sprite
                    # Ancrer le sprite au coin supérieur de la tuile
                    draw_x = screen_x - TILE_HALF_W
                    draw_y = screen_y - TILE_HALF_H
                    
                    self.screen.blit(sprite, (draw_x, draw_y))
                else:
                    # Fallback : Dessin du losange par couleur d'élévation
                    elev_idx = min(int(tile.elevation / 4), 4)
                    color = TERRAIN_COLORS.get(elev_idx, TERRAIN_COLORS[0])
                    points = [
                        (screen_x, base_y - TILE_HALF_H),
                        (screen_x + TILE_HALF_W, base_y),
                        (screen_x, base_y + TILE_HALF_H),
                        (screen_x - TILE_HALF_W, base_y)
                    ]
                    pygame.draw.polygon(self.screen, color, points)

                # 3. Effet 3D (pour les tuiles colorées)
                if height_offset > 0 and tile.terrain_type != 'water':
                     color = TERRAIN_COLORS.get(min(int(tile.elevation / 4), 4), TERRAIN_COLORS[0])
                     darker = (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40))
                     pygame.draw.polygon(self.screen, darker, [
                         (screen_x - TILE_HALF_W, base_y),
                         (screen_x, base_y + TILE_HALF_H),
                         (screen_x, screen_y + TILE_HALF_H),
                         (screen_x - TILE_HALF_W, screen_y)
                     ])

                # 4. DESSIN DU SPRITE D'ARBRE (après le sol pour qu'il soit par-dessus)
                is_tree = (x, y) in obstacles_dict and obstacles_dict[(x,y)] == "Tree"
                if is_tree and self.tree_sprite:
                    sprite = self.tree_sprite
                    # Ancrer le bas du sprite sur le point isométrique de la tuile
                    draw_x = screen_x - sprite.get_width() // 2
                    draw_y = screen_y - sprite.get_height()
                    self.screen.blit(sprite, (draw_x, draw_y))


    def draw_units(self, armies: list[Army]):
        """Dessine les unités."""
        all_units = []
        for army in armies:
            # Correction : L'armée contient une liste d'unités nommée 'units'
            for unit in army.units:
                if unit.is_alive:
                    all_units.append((army.army_id, unit))
        
        all_units.sort(key=lambda p: (round(p[1].pos[1]), round(p[1].pos[0])))

        for army_id, unit in all_units:
            x, y = unit.pos
            ix, iy = int(x), int(y)

            # Vérification limites (pour obtenir l'élévation)
            if 0 <= ix < self.map.width and 0 <= iy < self.map.height:
                 tile = self.map.grid[ix][iy]
            else:
                 continue 

            height_offset = 0
            if tile.terrain_type != 'water':
                 height_offset = int(tile.elevation) * 2

            screen_x, screen_y = self.cart_to_iso(x, y)
            # Position de dessin Y avec l'offset d'élévation
            unit_draw_y = screen_y - height_offset

            # Tentative de dessin du sprite
            unit_class = unit.__class__
            sprite_surface = self.unit_sprites.get(unit_class)


            if sprite_surface:
                 # Copie de la surface pour la teinter
                 final_surface = sprite_surface.copy()
                 
                 # Teinte pour différencier les armées
                 if army_id == 1: # Armée Rouge
                     final_surface.fill((255, 0, 0, 40), special_flags=pygame.BLEND_RGBA_MULT)
                 elif army_id == 0: # Armée Bleue
                     final_surface.fill((0, 0, 255, 40), special_flags=pygame.BLEND_RGBA_MULT)

                 # Centrer les pieds du sprite sur le point isométrique
                 draw_x = screen_x - final_surface.get_width() // 2
                 draw_y = unit_draw_y - final_surface.get_height() 
                 
                 self.screen.blit(final_surface, (draw_x, draw_y))
                 
                 # Position de la barre de vie sur le sprite
                 hp_y = unit_draw_y - final_surface.get_height() + 5 

            else:
                 # Fallback au dessin de cercle
                 color = BLUE if army_id == 0 else RED
                 pygame.draw.circle(self.screen, color, (screen_x, unit_draw_y - 10), 6)
                 hp_y = unit_draw_y - 25

            # Barres de vie
            hp_ratio = unit.current_hp / unit.max_hp
            pygame.draw.rect(self.screen, RED, (screen_x - 10, hp_y, 20, 3))
            pygame.draw.rect(self.screen, GREEN, (screen_x - 10, hp_y, 20 * hp_ratio, 3))


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
             text_color = BLUE if i == 0 else RED
             txt = self.font.render(f"Armée {i}: {alive} unités", True, text_color)
             self.screen.blit(txt, (20, y))
             y += 25

        # Minimap
        mm_x, mm_y = SCREEN_WIDTH - MINIMAP_SIZE - 20, SCREEN_HEIGHT - MINIMAP_SIZE - 20
        pygame.draw.rect(self.screen, BLACK, (mm_x, mm_y, MINIMAP_SIZE, MINIMAP_SIZE))
        
        scale_x = MINIMAP_SIZE / self.map.width
        scale_y = MINIMAP_SIZE / self.map.height

        for _, ox, oy in self.map.obstacles:
            # Dessine un petit carré de 2x2 pixels à la position de l'obstacle.
            rect_coords = (int(mm_x + ox*scale_x), int(mm_y + oy*scale_y), 2, 2)
            pygame.draw.rect(self.screen, (100,100,100), rect_coords) 
            
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