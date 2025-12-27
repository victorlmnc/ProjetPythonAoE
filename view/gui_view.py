import pygame
import os
import math
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

# Dimensions isométriques de BASE (Ratio 2:1)
BASE_TILE_WIDTH = 64
BASE_TILE_HEIGHT = 32

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

        # --- Zoom Settings ---
        self.min_zoom = 0.4
        self.max_zoom = 2.0
        self.zoom = self.min_zoom  # Démarrer dézoomé au max

        # Dimensions actuelles (seront calculées via update_zoom_metrics)
        self.tile_width = BASE_TILE_WIDTH
        self.tile_height = BASE_TILE_HEIGHT
        self.tile_half_w = self.tile_width // 2
        self.tile_half_h = self.tile_height // 2
        
        # Offsets d'affichage
        self.offset_x = 0
        self.offset_y = 0
        self.update_zoom_metrics()

        # --- Caméra ---
        self.scroll_speed = 15
        self.scroll_speed_fast = 45  # Vitesse avec Maj
        
        # Scroll initial au centre (0,0)
        self.scroll_x = 0
        self.scroll_y = 0
        
        # --- Toggles UI (Req 12 PDF: F1-F4) ---
        self.show_army_info = True      # F1: Infos générales
        self.show_hp_bars = True        # F2: Barres de vie
        self.show_minimap = True        # F3/M: Minimap
        self.show_unit_details = False  # F4: Détails unités
        
        # --- Drag souris pour scroll ---
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_scroll_start_x = 0
        self.drag_scroll_start_y = 0
        
        # --- LIGNES DE DÉBOGAGE POUR LES ARBRES ---
        # Ajout de plusieurs arbres à des positions fixes pour test
        self.map.add_obstacle("Tree", 10, 10) 
        self.map.add_obstacle("Tree", 15, 5)  
        self.map.add_obstacle("Tree", 5, 15)  
        self.map.add_obstacle("Tree", 20, 15) 
        # ----------------------------------------

        # --- Assets Originaux (Chargés une fois à taille de base) ---
        self.orig_grass: pygame.Surface | None = None
        self.orig_tree: pygame.Surface | None = None
        self.orig_units: dict = {}

        # --- Sprites Actuels (Redimensionnés selon zoom) ---
        self.unit_sprites: dict = {}
        self.tree_sprite: pygame.Surface | None = None
        self.grass_sprite: pygame.Surface | None = None
        
        self._load_sprites()
        print("Chargement des assets de fond terminé.")

    def update_zoom_metrics(self):
        """Recalcule les dimensions des tuiles et l'offset de base selon le zoom."""
        self.tile_width = int(BASE_TILE_WIDTH * self.zoom)
        self.tile_height = int(BASE_TILE_HEIGHT * self.zoom)
        self.tile_half_w = self.tile_width // 2
        self.tile_half_h = self.tile_height // 2

        # Recalcul de l'offset pour centrer la map (0,0 au centre théorique)
        center_map_x = self.map.width / 2
        center_map_y = self.map.height / 2
        iso_center_x = (center_map_x - center_map_y) * self.tile_half_w
        iso_center_y = (center_map_x + center_map_y) * self.tile_half_h
        self.offset_x = SCREEN_WIDTH / 2 - iso_center_x
        self.offset_y = SCREEN_HEIGHT / 2 - iso_center_y

    def _load_webp_asset(self, path: str, target_size: tuple[int, int], is_spritesheet: bool) -> pygame.Surface | None:
        """
        Charge un fichier WEBP via Pillow, le convertit en PNG in-memory,
        le charge dans Pygame, et le met à l'échelle vers la taille CIBLE.
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
        Charge tous les assets graphiques nécessaires dans self.orig_*.
        Ensuite, génère les versions scalées.
        """
        BASE_PATH = "assets" 
        
        # 1. Chargement des Originaux (Taille Zoom = 1.0)
        # Gazon
        grass_path = os.path.join(BASE_PATH, "resources/grass/grass.webp")
        self.orig_grass = self._load_webp_asset(
            grass_path, 
            target_size=(BASE_TILE_WIDTH, BASE_TILE_WIDTH // 2 + 16), 
            is_spritesheet=False
        ) 

        # Arbre
        tree_path = os.path.join(BASE_PATH, "resources/tree/Tree.webp")
        self.orig_tree = self._load_webp_asset(
            tree_path, 
            target_size=(60, 90), 
            is_spritesheet=False
        ) 
        
        # Unités - Chemins corrigés pour correspondre aux fichiers réels
        unit_configs = {
            Knight: (os.path.join(BASE_PATH, "units/knight/walk/knight_walk.webp"), 
                     (int(SPRITE_FRAME_WIDTH * 1.5), int(SPRITE_FRAME_HEIGHT * 1.5))),
            Crossbowman: (os.path.join(BASE_PATH, "units/crossbowman/walk/crossbowman_walk.webp"), 
                          (int(SPRITE_FRAME_WIDTH * 1.5), int(SPRITE_FRAME_HEIGHT * 1.5))),
            Pikeman: (os.path.join(BASE_PATH, "units/longswordman/walk/swordsman_walk.webp"), 
                      (int(SPRITE_FRAME_WIDTH * 1.5), int(SPRITE_FRAME_HEIGHT * 1.5))),
            LongSwordsman: (os.path.join(BASE_PATH, "units/longswordman/walk/swordsman_walk.webp"), 
                            (int(SPRITE_FRAME_WIDTH * 1.5), int(SPRITE_FRAME_HEIGHT * 1.5))),
        }
        
        self.orig_units = {}
        for unit_class, (path, size) in unit_configs.items():
            loaded = self._load_webp_asset(path, size, is_spritesheet=True)
            self.orig_units[unit_class] = loaded

        # 2. Génération des sprites à la taille actuelle
        self._rescale_assets()

    def _rescale_assets(self):
        """Redimensionne les assets originaux selon self.zoom."""
        if self.orig_grass:
            w, h = self.orig_grass.get_size()
            self.grass_sprite = pygame.transform.scale(self.orig_grass, (int(w * self.zoom), int(h * self.zoom)))
        
        if self.orig_tree:
            w, h = self.orig_tree.get_size()
            self.tree_sprite = pygame.transform.scale(self.orig_tree, (int(w * self.zoom), int(h * self.zoom)))

        self.unit_sprites = {}
        for u_class, surface in self.orig_units.items():
            if surface:
                w, h = surface.get_size()
                self.unit_sprites[u_class] = pygame.transform.scale(surface, (int(w * self.zoom), int(h * self.zoom)))

    def cart_to_iso(self, x: float, y: float) -> tuple[int, int]:
        """Convertit grille -> isométrique en tenant compte du zoom."""
        iso_x = (x - y) * self.tile_half_w
        iso_y = (x + y) * self.tile_half_h
        final_x = iso_x + self.offset_x - self.scroll_x
        final_y = iso_y + self.offset_y - self.scroll_y
        return int(final_x), int(final_y)

    def _clamp_camera(self):
        """Limite la caméra - plus de liberté quand zoomé pour atteindre les coins."""
        # Base: 300px | Zoomé max: ~1500px
        margin = int(300 + 750 * (self.zoom / self.min_zoom - 1))
        
        self.scroll_x = max(-margin, min(self.scroll_x, margin))
        self.scroll_y = max(-margin, min(self.scroll_y, margin))

    def check_events(self) -> str | None:
        """Gère clavier/souris."""
        keys = pygame.key.get_pressed()
        
        # Vitesse de scroll (Maj = rapide, Req 9 PDF)
        current_speed = self.scroll_speed_fast if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else self.scroll_speed
        
        # Déplacement Caméra
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.scroll_x -= current_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.scroll_x += current_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: self.scroll_y -= current_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s] and not (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]): 
            self.scroll_y += current_speed
        
        # Limiter la caméra aux bords de la carte
        self._clamp_camera()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            
            # --- DRAG SOURIS pour scroll (Clic droit + glisser) ---
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Clic droit
                self.is_dragging = True
                self.drag_start_x, self.drag_start_y = event.pos
                self.drag_scroll_start_x = self.scroll_x
                self.drag_scroll_start_y = self.scroll_y
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                self.is_dragging = False
            
            if event.type == pygame.MOUSEMOTION and self.is_dragging:
                dx = event.pos[0] - self.drag_start_x
                dy = event.pos[1] - self.drag_start_y
                self.scroll_x = self.drag_scroll_start_x - dx
                self.scroll_y = self.drag_scroll_start_y - dy
                self._clamp_camera()
            
            # --- GESTION DU ZOOM (MOUSEWHEEL) ---
            if event.type == pygame.MOUSEWHEEL:
                old_zoom = self.zoom
                if event.y > 0: # Scroll UP -> Zoom IN
                    self.zoom = min(self.zoom + 0.1, self.max_zoom)
                elif event.y < 0: # Scroll DOWN -> Zoom OUT
                    self.zoom = max(self.zoom - 0.1, self.min_zoom)
                
                if self.zoom != old_zoom:
                    self.update_zoom_metrics()
                    self._rescale_assets()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return "quit"
                if event.key == pygame.K_SPACE: return "toggle_pause"
                if event.key == pygame.K_s: return "step"
                
                # --- Req 12 PDF: F1-F4 Toggle info armée ---
                # F1/F2 capturées par Windows -> alternatives: touches 1 et 2
                if event.key == pygame.K_F1 or event.key == pygame.K_1: 
                    self.show_army_info = not self.show_army_info
                if event.key == pygame.K_F2 or event.key == pygame.K_2: 
                    self.show_hp_bars = not self.show_hp_bars
                if event.key == pygame.K_F3 or event.key == pygame.K_3: 
                    self.show_minimap = not self.show_minimap
                if event.key == pygame.K_F4 or event.key == pygame.K_4: 
                    self.show_unit_details = not self.show_unit_details
                
                # --- Req 11 PDF: M = toggle minimap ---
                if event.key == pygame.K_m:
                    self.show_minimap = not self.show_minimap
                
                # --- Raccourcis F9, F11, F12 (Requis par le PDF) ---
                if event.key == pygame.K_F9: return "switch_view"  # Basculer Terminal/Pygame
                if event.key == pygame.K_F11: return "quick_save"  # Sauvegarde rapide
                if event.key == pygame.K_F12: return "quick_load"  # Chargement rapide

                # --- Req 10 (Variable Speed L.422) ---
                if event.key == pygame.K_KP_PLUS or event.key == pygame.K_PLUS: return "speed_up"
                if event.key == pygame.K_KP_MINUS or event.key == pygame.K_MINUS: return "speed_down"
        return None

    def draw_map(self):
        """Dessine le sol et les obstacles."""
        
        obstacles_dict = {(int(x), int(y)): type_name for type_name, x, y in self.map.obstacles}

        for y in range(self.map.height):
            for x in range(self.map.width):
                tile = self.map.grid[x][y]
                
                screen_x, screen_y = self.cart_to_iso(x, y)
                
                # Optimisation : ne pas dessiner hors écran (ajusté avec zoom)
                margin = 100 * self.zoom
                if not (-margin < screen_x < SCREEN_WIDTH + margin and -margin < screen_y < SCREEN_HEIGHT + margin):
                   continue

                # 1. Calcul de l'élévation (mise à l'échelle)
                height_offset = 0
                if tile.terrain_type != 'water':
                    # Hauteur standard * zoom
                    height_offset = int(tile.elevation * 2 * self.zoom)
                    
                base_y = screen_y - height_offset

                # 2. DESSIN DU FOND (GAZON ou COULEUR)
                if self.grass_sprite and tile.terrain_type != 'water' and tile.elevation == 0:
                    sprite = self.grass_sprite
                    # Ancrer le sprite au coin supérieur de la tuile
                    draw_x = screen_x - self.tile_half_w
                    draw_y = screen_y - self.tile_half_h
                    
                    self.screen.blit(sprite, (draw_x, draw_y))
                else:
                    # Fallback : Dessin du losange par couleur d'élévation
                    elev_idx = min(int(tile.elevation / 4), 4)
                    color = TERRAIN_COLORS.get(elev_idx, TERRAIN_COLORS[0])
                    points = [
                        (screen_x, base_y - self.tile_half_h),
                        (screen_x + self.tile_half_w, base_y),
                        (screen_x, base_y + self.tile_half_h),
                        (screen_x - self.tile_half_w, base_y)
                    ]
                    pygame.draw.polygon(self.screen, color, points)

                # 3. Effet 3D (pour les tuiles colorées)
                if height_offset > 0 and tile.terrain_type != 'water':
                     color = TERRAIN_COLORS.get(min(int(tile.elevation / 4), 4), TERRAIN_COLORS[0])
                     darker = (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40))
                     pygame.draw.polygon(self.screen, darker, [
                         (screen_x - self.tile_half_w, base_y),
                         (screen_x, base_y + self.tile_half_h),
                         (screen_x, screen_y + self.tile_half_h),
                         (screen_x - self.tile_half_w, screen_y)
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
                 height_offset = int(tile.elevation * 2 * self.zoom)

            screen_x, screen_y = self.cart_to_iso(x, y)
            # Position de dessin Y avec l'offset d'élévation
            unit_draw_y = screen_y - height_offset

            # Tentative de dessin du sprite
            unit_class = unit.__class__
            sprite_surface = self.unit_sprites.get(unit_class)

            # Sprite is now enabled


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
                 # Fallback au dessin de cercle (TOUJOURS visible)
                 color = BLUE if army_id == 0 else RED
                 radius = max(8, int(10 * self.zoom))  # Minimum 8 pixels
                 circle_y = unit_draw_y - int(15 * self.zoom)
                 pygame.draw.circle(self.screen, color, (screen_x, circle_y), radius)
                 # Ajouter un contour blanc pour la visibilité
                 pygame.draw.circle(self.screen, WHITE, (screen_x, circle_y), radius, 2)
                 hp_y = circle_y - radius - 5

            # Barres de vie (F2 toggle)
            if self.show_hp_bars:
                hp_ratio = unit.current_hp / unit.max_hp
                
                bar_width = int(20 * self.zoom)
                bar_height = int(3 * self.zoom)
                
                pygame.draw.rect(self.screen, RED, (screen_x - bar_width//2, hp_y, bar_width, bar_height))
                pygame.draw.rect(self.screen, GREEN, (screen_x - bar_width//2, hp_y, bar_width * hp_ratio, bar_height))


    def draw_ui(self, turn_count, paused, armies):
        """Interface Utilisateur avec toggles F1-F4."""
        if paused:
            txt = self.ui_font.render("PAUSE (Espace pour reprendre)", True, WHITE, RED)
            self.screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 20))
        
        turn_txt = self.ui_font.render(f"Tour: {turn_count}", True, WHITE)
        self.screen.blit(turn_txt, (20, 20))

        # F1: Infos générales armée
        if self.show_army_info:
            y = 60
            for i, army in enumerate(armies):
                alive = sum(1 for u in army.units if u.is_alive)
                total_hp = sum(u.current_hp for u in army.units if u.is_alive)
                text_color = BLUE if i == 0 else RED
                general_name = army.general.__class__.__name__
                txt = self.font.render(f"Armée {i+1} [{general_name}]: {alive} unités | HP: {total_hp}", True, text_color)
                self.screen.blit(txt, (20, y))
                y += 25
        
        # F4: Détails unités (types et nombres)
        if self.show_unit_details:
            y = 130
            for i, army in enumerate(armies):
                text_color = BLUE if i == 0 else RED
                unit_counts = {}
                for u in army.units:
                    if u.is_alive:
                        name = u.__class__.__name__
                        unit_counts[name] = unit_counts.get(name, 0) + 1
                
                header = self.font.render(f"Armée {i+1} détail:", True, text_color)
                self.screen.blit(header, (20, y))
                y += 20
                for unit_type, count in unit_counts.items():
                    txt = self.font.render(f"  {unit_type}: {count}", True, text_color)
                    self.screen.blit(txt, (20, y))
                    y += 18
                y += 10
        
        # Afficher les raccourcis actifs
        shortcuts = f"1:Info 2:HP 3/M:Minimap 4:Détails"
        shortcut_txt = self.font.render(shortcuts, True, (150, 150, 150))
        self.screen.blit(shortcut_txt, (SCREEN_WIDTH - shortcut_txt.get_width() - 20, 20))

        # Minimap (F3/M toggle)
        if self.show_minimap:
            mm_x, mm_y = SCREEN_WIDTH - MINIMAP_SIZE - 20, SCREEN_HEIGHT - MINIMAP_SIZE - 20
            pygame.draw.rect(self.screen, BLACK, (mm_x, mm_y, MINIMAP_SIZE, MINIMAP_SIZE))
            
            scale_x = MINIMAP_SIZE / self.map.width
            scale_y = MINIMAP_SIZE / self.map.height

            for _, ox, oy in self.map.obstacles:
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