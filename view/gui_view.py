import pygame
import os
import math
from io import BytesIO
from PIL import Image

from core.map import Map
from core.army import Army
# Import de toutes les classes d'unités pour le mappage des sprites
from core.unit import (
    Knight, Pikeman, Crossbowman, LongSwordsman, LightCavalry, 
    Castle, Wonder, Unit
)

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
        self.min_zoom = 0.2  # déZoom loin
        self.max_zoom = 2.0
        # Discrete zoom levels for caching (performance optimization)
        self.zoom_levels = [0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0]
        self.zoom = self.min_zoom  # Démarrer dézoomé au max
        # Cache for pre-scaled sprites at each zoom level
        self._zoom_cache: dict[float, dict] = {}

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
        self.show_unit_details = True  # F4: Détails unités
        
        # --- Drag souris pour scroll ---
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_scroll_start_x = 0
        self.drag_scroll_start_y = 0
        
        # Debug obstacles removed for production

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
        # timing pour les animations côté vue (ms)
        self._last_anim_tick = pygame.time.get_ticks()
        # Facteur pour ralentir l'animation côté vue (>1 = plus lent)
        self.anim_time_scale = 0.5

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
        Charge un fichier WEBP via Pillow, convertit en raw bytes,
        charge dans Pygame, et met à l'échelle vers la taille CIBLE.
        Optimisé pour éviter l'encodage PNG.
        """
        try:
            pil_img = Image.open(path).convert("RGBA")
            
            if is_spritesheet:
                # Découpe la première frame (position 0,0)
                frame_area = (0, 0, SPRITE_FRAME_WIDTH, SPRITE_FRAME_HEIGHT)
                pil_img = pil_img.crop(frame_area)
            
            # Conversion Pillow -> Bytes (Raw RGBA) -> Pygame Surface
            mode = pil_img.mode
            size = pil_img.size
            data = pil_img.tobytes()
            
            surface = pygame.image.frombytes(data, size, mode).convert_alpha()

            # Mise à l'échelle (pour l'affichage isométrique)
            return pygame.transform.scale(surface, target_size)

        except FileNotFoundError:
            print(f"Erreur FATALE: Fichier non trouvé: {path}")
            return None
        except Exception as e:
            print(f"Erreur de chargement de l'asset {path}: {e}")
            return None

    def _load_spritesheet_grid(self, path: str, rows: int, cols: int) -> list[list[pygame.Surface]] | None:
        """Charge une spritesheet WebP et découpe en grille [rows][cols].
        Retourne une liste de listes: frames[row][col].
        Optimisé via tobytes/frombytes.
        """
        try:
            pil_img = Image.open(path).convert("RGBA")
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Erreur ouverture spritesheet {path}: {e}")
            return None

        sheet_w, sheet_h = pil_img.size
        # Déduire la taille d'une frame si possible
        frame_w = sheet_w // cols if cols > 0 else 0
        frame_h = sheet_h // rows if rows > 0 else 0
        if frame_w <= 0 or frame_h <= 0:
            return None

        frames: list[list[pygame.Surface]] = []
        for r in range(rows):
            row_frames: list[pygame.Surface] = []
            for c in range(cols):
                left = c * frame_w
                upper = r * frame_h
                right = left + frame_w
                lower = upper + frame_h
                try:
                    frame = pil_img.crop((left, upper, right, lower))
                    
                    mode = frame.mode
                    size = frame.size
                    data = frame.tobytes()
                    surf = pygame.image.frombytes(data, size, mode).convert_alpha()
                    
                    row_frames.append(surf)
                except Exception:
                    # ignorer frame invalide
                    continue
            frames.append(row_frames)
        return frames

    def _load_cache_frames(self, cache_dir: str, target_size: tuple[int,int]) -> list[pygame.Surface] | None:
        """Charge les images individuelles dans `assets/.cache/<name>`.
        Renvoie une liste de Surfaces déjà mises à l'échelle, ou None si aucun fichier.
        """
        try:
            if not os.path.isdir(cache_dir):
                return None
            files = sorted(f for f in os.listdir(cache_dir) if f.lower().endswith(('.png', '.webp', '.jpg', '.jpeg'))) 
            frames: list[pygame.Surface] = []
            for fn in files:
                path = os.path.join(cache_dir, fn)
                try:
                    pil = Image.open(path).convert("RGBA")
                    mode = pil.mode
                    size = pil.size
                    data = pil.tobytes()
                    surf = pygame.image.frombytes(data, size, mode).convert_alpha()
                    
                    surf = pygame.transform.scale(surf, target_size)
                    frames.append(surf)
                except Exception:
                    # Ignorer les fichiers invalides
                    continue
            return frames if frames else None
        except Exception as e:
            print(f"Erreur lors du chargement du cache {cache_dir}: {e}")
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
        
        # Chargement des assets d'unités : par unité, par couleur, par état.
        # Structure stockée : self.orig_units[unit_class][color][state] = frames[row][col]
        unit_configs = {
            Knight: "knight",
            Crossbowman: "crossbowman",
            Pikeman: "pikeman",
            LongSwordsman: "longswordman",
            LightCavalry: "knight", # Fallback to knight sprites
        }

        states_grid = {
            'death': (24, 30),
            'idle': (24, 30),
            'walk': (16, 30),
            'attack': (16, 30),
        }

        self.orig_units = {}
        for u_class, name in unit_configs.items():
            self.orig_units[u_class] = {'blue': {}, 'red': {}}
            for color_folder, prefix in (('blue', 'b'), ('red', 'r')):
                for state, (rows, cols) in states_grid.items():
                    # Filename pattern observed: b_knight_walk.webp
                    filename = f"{prefix}_{name}_{state}.webp"
                    path = os.path.join(BASE_PATH, 'units', name, color_folder, filename)
                    frames = self._load_spritesheet_grid(path, rows, cols)
                    if frames:
                        self.orig_units[u_class][color_folder][state] = frames
                    else:
                        # no frames found for this state/color
                        self.orig_units[u_class][color_folder][state] = None

        # 2. Génération des sprites à la taille actuelle
        self._rescale_assets()

    def _get_cached_zoom_level(self, zoom: float) -> float:
        """Trouve le niveau de zoom caché le plus proche."""
        return min(self.zoom_levels, key=lambda z: abs(z - zoom))

    def _rescale_assets(self):
        """Redimensionne les assets originaux selon self.zoom avec cache."""
        # Snap to nearest cached zoom level for performance
        cached_zoom = self._get_cached_zoom_level(self.zoom)
        
        # Check if we already have this zoom level cached
        if cached_zoom in self._zoom_cache:
            cache = self._zoom_cache[cached_zoom]
            self.grass_sprite = cache.get('grass')
            self.tree_sprite = cache.get('tree')
            self.unit_sprites = cache.get('units', {})
            return
        
        # Create new cache entry
        cache = {}
        
        # Use smoothscale for better quality at low zoom levels
        scale_func = pygame.transform.smoothscale if cached_zoom < 0.6 else pygame.transform.scale
        
        if self.orig_grass:
            w, h = self.orig_grass.get_size()
            cache['grass'] = scale_func(self.orig_grass, (max(1, int(w * cached_zoom)), max(1, int(h * cached_zoom))))
        
        if self.orig_tree:
            w, h = self.orig_tree.get_size()
            cache['tree'] = scale_func(self.orig_tree, (max(1, int(w * cached_zoom)), max(1, int(h * cached_zoom))))

        # Scale unit sprites
        DISPLAY_SCALE = 1.5
        unit_cache = {}
        for u_class, color_dict in self.orig_units.items():
            unit_cache[u_class] = {'blue': {}, 'red': {}}
            for color in ('blue', 'red'):
                for state, frames in (color_dict.get(color) or {}).items():
                    if not frames:
                        unit_cache[u_class][color][state] = None
                        continue
                    scaled_orientations = []
                    target_w = max(1, int(SPRITE_FRAME_WIDTH * DISPLAY_SCALE * cached_zoom))
                    target_h = max(1, int(SPRITE_FRAME_HEIGHT * DISPLAY_SCALE * cached_zoom))
                    for row_frames in frames:
                        scaled_row = []
                        for frame in row_frames:
                            try:
                                scaled = scale_func(frame, (target_w, target_h))
                                scaled_row.append(scaled)
                            except Exception:
                                scaled_row.append(frame)
                        scaled_orientations.append(scaled_row)
                    unit_cache[u_class][color][state] = scaled_orientations
        
        cache['units'] = unit_cache
        
        # Store in cache and apply
        self._zoom_cache[cached_zoom] = cache
        self.grass_sprite = cache.get('grass')
        self.tree_sprite = cache.get('tree')
        self.unit_sprites = unit_cache

    def cart_to_iso(self, x: float, y: float) -> tuple[int, int]:
        """Convertit grille -> isométrique en tenant compte du zoom."""
        iso_x = (x - y) * self.tile_half_w
        iso_y = (x + y) * self.tile_half_h
        final_x = iso_x + self.offset_x - self.scroll_x
        final_y = iso_y + self.offset_y - self.scroll_y
        # Use round() to reduce animation vibration at low zoom
        return round(final_x), round(final_y)

    def iso_to_cart(self, iso_x: float, iso_y: float) -> tuple[float, float]:
        """Convertit écran isométrique -> grille cartésienne (inverse de cart_to_iso)."""
        # Annuler le scroll/offset
        adj_x = iso_x - self.offset_x + self.scroll_x
        adj_y = iso_y - self.offset_y + self.scroll_y
        
        # Système d'équations:
        # iso_x = (x - y) * tile_half_w
        # iso_y = (x + y) * tile_half_h
        # => x - y = adj_x / tile_half_w
        # => x + y = adj_y / tile_half_h
        # => 2x = adj_x/thw + adj_y/thh
        
        term1 = adj_x / self.tile_half_w
        term2 = adj_y / self.tile_half_h
        
        x = (term1 + term2) / 2
        y = (term2 - term1) / 2
        return x, y

    def _clamp_camera(self):
        """Limite la caméra dynamiquement selon la taille de la carte et le zoom."""
        # Calcul de la taille projetée de la carte (demi-diagonales)
        # Largeur totale iso ~ (W + H) * tile_half_w
        # Hauteur totale iso ~ (W + H) * tile_half_h
        
        # On autorise à scroller jusqu'à voir les coins + une marge (écran/2)
        limit_x = (self.map.width + self.map.height) * self.tile_half_w / 2 + SCREEN_WIDTH * 0.2
        limit_y = (self.map.width + self.map.height) * self.tile_half_h / 2 + SCREEN_HEIGHT * 0.2
        
        self.scroll_x = max(-limit_x, min(self.scroll_x, limit_x))
        self.scroll_y = max(-limit_y, min(self.scroll_y, limit_y))

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
        """Dessine le sol et les obstacles avec view frustum culling."""
        
        obstacles_dict = {(int(x), int(y)): type_name for type_name, x, y in self.map.obstacles}
        
        # --- VIEW FRUSTUM CULLING ---
        # Calculate visible tile range from screen corners (optimization)
        margin = 100 * self.zoom
        
        # Get cart coords of screen corners
        top_left = self.iso_to_cart(-margin, -margin)
        top_right = self.iso_to_cart(SCREEN_WIDTH + margin, -margin)
        bottom_left = self.iso_to_cart(-margin, SCREEN_HEIGHT + margin)
        bottom_right = self.iso_to_cart(SCREEN_WIDTH + margin, SCREEN_HEIGHT + margin)
        
        # Find bounding box in tile coordinates
        all_x = [top_left[0], top_right[0], bottom_left[0], bottom_right[0]]
        all_y = [top_left[1], top_right[1], bottom_left[1], bottom_right[1]]
        
        min_tile_x = max(0, int(min(all_x)) - 1)
        max_tile_x = min(self.map.width, int(max(all_x)) + 2)
        min_tile_y = max(0, int(min(all_y)) - 1)
        max_tile_y = min(self.map.height, int(max(all_y)) + 2)
        
        # Only iterate through visible tiles
        for y in range(min_tile_y, max_tile_y):
            for x in range(min_tile_x, max_tile_x):
                tile = self.map.grid[x][y]
                screen_x, screen_y = self.cart_to_iso(x, y)

                # 1. Calcul de l'élévation (mise à l'échelle)
                height_offset = 0
                if tile.terrain_type != 'water':
                    height_offset = round(tile.elevation * 2 * self.zoom)
                    
                base_y = screen_y - height_offset

                # 2. DESSIN DU FOND (GAZON ou COULEUR)
                if self.grass_sprite and tile.terrain_type != 'water' and tile.elevation == 0:
                    sprite = self.grass_sprite
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

                # 4. DESSIN DU SPRITE D'ARBRE
                is_tree = (x, y) in obstacles_dict and obstacles_dict[(x,y)] == "Tree"
                if is_tree and self.tree_sprite:
                    sprite = self.tree_sprite
                    draw_x = screen_x - sprite.get_width() // 2
                    draw_y = screen_y - sprite.get_height()
                    self.screen.blit(sprite, (draw_x, draw_y))


    def draw_units(self, armies: list[Army]):
        """Affiche les unités avec animations extraites des spritesheets.

        Structure attendue : self.unit_sprites[UnitClass][color][state][orientation][frame]
        color = 'blue' pour army_id==0 sinon 'red'.
        """
        visible_units = []
        for army in armies:
            for unit in army.units:
                # Inclure aussi les unités mortes récentes pour afficher l'animation de mort
                visible_units.append((army.army_id, unit))

        visible_units.sort(key=lambda p: (round(p[1].pos[1]), round(p[1].pos[0])))

        for army_id, unit in visible_units:
            x, y = unit.pos
            ix, iy = int(x), int(y)
            if not (0 <= ix < self.map.width and 0 <= iy < self.map.height):
                continue

            tile = self.map.grid[ix][iy]
            height_offset = 0
            if tile.terrain_type != 'water':
                height_offset = int(tile.elevation * 2 * self.zoom)

            screen_x, screen_y = self.cart_to_iso(x, y)
            unit_draw_y = screen_y - height_offset

            unit_class = unit.__class__
            sprites_for_unit = self.unit_sprites.get(unit_class)
            color_key = 'blue' if army_id == 0 else 'red'

            # normaliser nom d'état
            state = getattr(unit, 'statut', 'idle')
            if state == 'statique':
                state = 'idle'

            current_frame = None
            if sprites_for_unit:
                frames_for_color = sprites_for_unit.get(color_key, {})
                frames_orient = frames_for_color.get(state)
                if frames_orient:
                    # estimer orientation : privilégier la cible si présente, sinon last_pos
                    # calculer l'angle en espace écran (isométrique) pour correspondre à l'orientation des sprites
                    tgt = None
                    target_id = getattr(unit, 'target_id', None)
                    if target_id is not None:
                        for a in armies:
                            for uu in a.units:
                                if uu.unit_id == target_id:
                                    tgt = uu
                                    break
                            if tgt: break

                    if tgt is not None:
                        u_xs, u_ys = self.cart_to_iso(unit.pos[0], unit.pos[1])
                        t_xs, t_ys = self.cart_to_iso(tgt.pos[0], tgt.pos[1])
                        vx = t_xs - u_xs
                        vy = t_ys - u_ys
                    else:
                        lx, ly = getattr(unit, 'last_pos', unit.pos)
                        u_xs, u_ys = self.cart_to_iso(unit.pos[0], unit.pos[1])
                        l_xs, l_ys = self.cart_to_iso(lx, ly)
                        vx = u_xs - l_xs
                        vy = u_ys - l_ys

                    if abs(vx) < 1e-3 and abs(vy) < 1e-3:
                        orient_idx = 0
                    else:
                        angle = math.degrees(math.atan2(vy, vx)) % 360
                        rows = len(frames_orient)
                        sector = 360.0 / max(1, rows)
                        orient_idx = int((angle + sector/2) // sector) % rows

                    nframes = len(frames_orient[orient_idx]) if frames_orient[orient_idx] else 0
                    if nframes > 0:
                        if state == 'death' and not unit.is_alive:
                            idx = min(getattr(unit, 'anim_index', 0), nframes - 1)
                        else:
                            idx = getattr(unit, 'anim_index', 0) % nframes
                        try:
                            current_frame = frames_orient[orient_idx][idx]
                        except Exception:
                            current_frame = None

            if current_frame:
                surf = current_frame
                draw_x = screen_x - surf.get_width() // 2
                draw_y = unit_draw_y - surf.get_height()
                self.screen.blit(surf, (draw_x, draw_y))
                hp_y = unit_draw_y - surf.get_height() + 5
            else:
                # fallback minimal: dessiner seulement si l'unité est vivante
                if unit.is_alive:
                    color = BLUE if army_id == 0 else RED
                    
                    # Logique de dessin de fallback (Cercle vs Carré)
                    # Si c'est un Bâtiment (hitbox > 0.6 ou type spécifique), on fait un carré/rectangle
                    is_building = unit.hitbox_radius > 0.6
                    
                    if is_building:
                        # Dessin de bâtiment (Carré 3D simple)
                        size = int(unit.hitbox_radius * 2 * 32 * self.zoom) # 32 pixels/mètre approx
                        rect_x = screen_x - size // 2
                        rect_y = unit_draw_y - size
                        
                        # Couleur spécifique pour Castle/Wonder
                        if isinstance(unit, Castle):
                            draw_color = (150, 150, 150) # Gris Pierre
                        elif isinstance(unit, Wonder):
                            draw_color = (255, 215, 0) # Or
                        else:
                            draw_color = color
                            
                        # Face avant
                        pygame.draw.rect(self.screen, draw_color, (rect_x, rect_y, size, size))
                        # Bordure
                        pygame.draw.rect(self.screen, BLACK, (rect_x, rect_y, size, size), 2)
                        
                        # Marque de couleur du joueur
                        mark_size = size // 4
                        pygame.draw.rect(self.screen, color, (rect_x + size//2 - mark_size//2, rect_y + size//4, mark_size, mark_size))

                        hp_y = rect_y - 10
                    else:
                        # Dessin d'unité standard (Cercle)
                        radius = max(8, int(10 * self.zoom))
                        circle_y = unit_draw_y - int(15 * self.zoom)
                        pygame.draw.circle(self.screen, color, (screen_x, circle_y), radius)
                        pygame.draw.circle(self.screen, WHITE, (screen_x, circle_y), radius, 2)
                        hp_y = circle_y - radius - 5
                else:
                    # unité morte et pas de sprite: ne rien dessiner
                    hp_y = unit_draw_y

            if self.show_hp_bars and unit.is_alive:
                hp_ratio = unit.current_hp / unit.max_hp if unit.max_hp > 0 else 0
                bar_width = int(24 * self.zoom)
                bar_height = int(4 * self.zoom)
                pygame.draw.rect(self.screen, RED, (screen_x - bar_width//2, hp_y, bar_width, bar_height))
                pygame.draw.rect(self.screen, GREEN, (screen_x - bar_width//2, hp_y, int(bar_width * hp_ratio), bar_height))


    def draw_ui(self, time_elapsed, paused, armies):
        """Interface Utilisateur avec toggles F1-F4 - Design moderne."""
        
        # --- PAUSE INDICATOR ---
        if paused:
            pause_surface = pygame.Surface((400, 50), pygame.SRCALPHA)
            pause_surface.fill((200, 50, 50, 200))
            txt = self.ui_font.render("⏸ PAUSE - Espace pour reprendre", True, WHITE)
            pause_surface.blit(txt, (pause_surface.get_width()//2 - txt.get_width()//2, 12))
            self.screen.blit(pause_surface, (SCREEN_WIDTH//2 - 200, 20))
        
        # --- TIME DISPLAY (Top left corner) ---
        time_surface = pygame.Surface((120, 40), pygame.SRCALPHA)
        time_surface.fill((0, 0, 0, 150))
        time_txt = self.ui_font.render(f"⏱ {int(time_elapsed)}s", True, WHITE)
        time_surface.blit(time_txt, (10, 8))
        self.screen.blit(time_surface, (15, 15))

        # --- F1: ARMY INFO PANELS ---
        if self.show_army_info:
            panel_width = 280
            panel_height = 70
            panel_x = 15
            panel_y = 65
            
            for i, army in enumerate(armies):
                alive = sum(1 for u in army.units if u.is_alive)
                total = len(army.units)
                percent = (alive / total) if total > 0 else 0
                total_hp = sum(u.current_hp for u in army.units if u.is_alive)
                max_total_hp = sum(u.max_hp for u in army.units)
                hp_percent = (total_hp / max_total_hp) if max_total_hp > 0 else 0
                general_name = army.general.__class__.__name__
                
                # Team colors
                team_color = (70, 130, 220) if i == 0 else (220, 70, 70)
                accent_color = (100, 160, 255) if i == 0 else (255, 100, 100)
                
                # Panel background
                panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
                panel.fill((20, 20, 25, 220))
                
                # Team color accent bar (left side)
                pygame.draw.rect(panel, team_color, (0, 0, 4, panel_height))
                
                # Header
                header = self.font.render(f"Armée {i+1} • {general_name}", True, accent_color)
                panel.blit(header, (12, 8))
                
                # Units count with mini progress bar
                units_txt = self.font.render(f"Unités: {alive}/{total}", True, WHITE)
                panel.blit(units_txt, (12, 30))
                
                # Units progress bar
                bar_x, bar_y, bar_w, bar_h = 110, 33, 80, 10
                pygame.draw.rect(panel, (40, 40, 45), (bar_x, bar_y, bar_w, bar_h))
                pygame.draw.rect(panel, accent_color, (bar_x, bar_y, int(bar_w * percent), bar_h))
                
                # HP display
                hp_txt = self.font.render(f"HP: {total_hp}", True, (150, 255, 150))
                panel.blit(hp_txt, (200, 30))
                
                # HP progress bar (bottom)
                hp_bar_y = panel_height - 12
                pygame.draw.rect(panel, (40, 40, 45), (12, hp_bar_y, panel_width - 24, 6))
                pygame.draw.rect(panel, (100, 200, 100), (12, hp_bar_y, int((panel_width - 24) * hp_percent), 6))
                
                self.screen.blit(panel, (panel_x, panel_y + i * (panel_height + 10)))
        
        # --- F4: UNIT DETAILS PANELS ---
        if self.show_unit_details:
            detail_panel_width = 200
            detail_x = 15
            detail_y = 220 if self.show_army_info else 65
            
            for i, army in enumerate(armies):
                team_color = (70, 130, 220) if i == 0 else (220, 70, 70)
                accent_color = (100, 160, 255) if i == 0 else (255, 100, 100)
                
                # Count units by type
                unit_counts = {}
                for u in army.units:
                    name = u.__class__.__name__
                    if name not in unit_counts:
                        unit_counts[name] = {'alive': 0, 'total': 0}
                    unit_counts[name]['total'] += 1
                    if u.is_alive:
                        unit_counts[name]['alive'] += 1
                
                # Calculate panel height
                num_types = len(unit_counts)
                detail_panel_height = 30 + num_types * 22
                
                # Panel background
                panel = pygame.Surface((detail_panel_width, detail_panel_height), pygame.SRCALPHA)
                panel.fill((20, 20, 25, 200))
                pygame.draw.rect(panel, team_color, (0, 0, 3, detail_panel_height))
                
                # Header
                header = self.font.render(f"Armée {i+1} - Détails", True, accent_color)
                panel.blit(header, (10, 6))
                
                # Unit type rows
                row_y = 28
                # Unit type icons (simple text)
                UNIT_ICONS = {
                    'Knight': '⚔', 'Pikeman': '🔱', 'Crossbowman': '🏹',
                    'LongSwordsman': '⚔', 'LightCavalry': '🐎', 'Castle': '🏰',
                    'Wonder': '⭐', 'Onager': '💥', 'Monk': '✝'
                }
                
                for unit_type, counts in unit_counts.items():
                    icon = UNIT_ICONS.get(unit_type, '•')
                    alive, total = counts['alive'], counts['total']
                    ratio = alive / total if total > 0 else 0
                    
                    # Status color
                    if ratio == 1:
                        status_color = (100, 200, 100)  # Full = green
                    elif ratio > 0.5:
                        status_color = (200, 200, 100)  # Half = yellow
                    elif ratio > 0:
                        status_color = (200, 100, 100)  # Low = red
                    else:
                        status_color = (100, 100, 100)  # Dead = gray
                    
                    # Short name (max 10 chars)
                    short_name = unit_type[:10] if len(unit_type) > 10 else unit_type
                    line = self.font.render(f"{icon} {short_name}: {alive}/{total}", True, status_color)
                    panel.blit(line, (10, row_y))
                    row_y += 20
                
                self.screen.blit(panel, (detail_x, detail_y))
                detail_y += detail_panel_height + 10
        
        # --- SHORTCUTS DISPLAY (Top right) ---
        shortcuts_surface = pygame.Surface((220, 30), pygame.SRCALPHA)
        shortcuts_surface.fill((0, 0, 0, 120))
        shortcuts = "1:Info 2:HP 3:Map 4:Detail"
        shortcut_txt = self.font.render(shortcuts, True, (150, 150, 150))
        shortcuts_surface.blit(shortcut_txt, (10, 6))
        self.screen.blit(shortcuts_surface, (SCREEN_WIDTH - 235, 15))

        # Minimap (F3/M toggle)
        if self.show_minimap:
            # Centre de la minimap
            mm_center_x = SCREEN_WIDTH - MINIMAP_SIZE/2 - 20
            mm_center_y = SCREEN_HEIGHT - MINIMAP_SIZE/2 - 20
            
            # Facteur d'échelle pour faire rentrer la map (diagonale W+H) dans MINIMAP_SIZE
            # Map Dimensions: W, H
            # Diagonale Isométrique Max ~ W + H (en "unités de grille")
            # Marges de sécurité
            max_dim = self.map.width + self.map.height
            scale_mm = (MINIMAP_SIZE * 0.8) / max_dim
            
            # Fonction locale pour projeter sur la minimap
            def cart_to_mm(cx, cy):
                # Iso projection standard mais centrée sur mm_center
                # x_iso = (x - y)
                # y_iso = (x + y)
                iso_x = (cx - cy) * scale_mm
                iso_y = (cx + cy) * scale_mm * 0.5 # Aplatissement standard 2:1
                return int(mm_center_x + iso_x), int(mm_center_y + iso_y - (self.map.width + self.map.height)*scale_mm*0.25)
                # Le -offset Y sert à centrer approximativement le losange

            # 1. Dessiner le losange de fond (Grille 0,0 -> W,0 -> W,H -> 0,H)
            p1 = cart_to_mm(0, 0)
            p2 = cart_to_mm(self.map.width, 0)
            p3 = cart_to_mm(self.map.width, self.map.height)
            p4 = cart_to_mm(0, self.map.height)
            
            pygame.draw.polygon(self.screen, (20, 20, 20), [p1, p2, p3, p4]) # Fond sombre
            pygame.draw.polygon(self.screen, (100, 100, 100), [p1, p2, p3, p4], 2) # Bordure

            # 2. Dessiner les unités
            for army in armies:
                c = BLUE if army.army_id == 0 else RED
                for u in army.units:
                    if u.is_alive:
                        mx, my = cart_to_mm(u.pos[0], u.pos[1])
                        # Petit point
                        pygame.draw.circle(self.screen, c, (mx, my), 2)

            # 3. Dessiner le rectangle de vue caméra (Viewport)
            # On projette les 4 coins de l'écran vers le monde (grid), puis vers la minimap
            corners_screen = [
                (0, 0),
                (SCREEN_WIDTH, 0),
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                (0, SCREEN_HEIGHT)
            ]
            
            poly_points = []
            for sx, sy in corners_screen:
                gx, gy = self.iso_to_cart(sx, sy)
                # Clamp aux bords pour éviter que le rect parte à l'infini graphiquement
                gx = max(0, min(self.map.width, gx))
                gy = max(0, min(self.map.height, gy))
                poly_points.append(cart_to_mm(gx, gy))
            
            if len(poly_points) == 4:
                pygame.draw.polygon(self.screen, WHITE, poly_points, 1)

    def display(self, armies: list[Army], time_elapsed: float, paused: bool) -> str | None:
        cmd = self.check_events()

        # Avancer les animations par frame (déléguer à la vue pour fluidité)
        now = pygame.time.get_ticks()
        delta = now - getattr(self, '_last_anim_tick', now)
        self._last_anim_tick = now
        # Appliquer le facteur de ralentissement (diviser le delta pour ralentir)
        try:
            scaled_delta = max(1, int(delta / max(0.001, self.anim_time_scale)))
        except Exception:
            scaled_delta = max(1, int(delta))
        # Si le jeu est en pause, ne pas avancer les animations
        if not paused:
            try:
                for army in armies:
                    for unit in army.units:
                        try:
                            unit.tick_animation(int(scaled_delta))
                        except Exception:
                            pass
            except Exception:
                pass

        self.screen.fill(BG_COLOR)
        self.draw_map()
        self.draw_units(armies)
        self.draw_ui(time_elapsed, paused, armies)
        pygame.display.flip()
        self.clock.tick(60)
        return cmd