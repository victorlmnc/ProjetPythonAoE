import pygame
import sys
from core.map import Map
from core.unit import Unit, Knight, Pikeman, Crossbowman
from core.army import Army

class PygameView:    
    # Couleurs
    COLOR_BG = (30, 30, 30)
    COLOR_GRID = (50, 50, 50)
    COLOR_TEXT = (255, 255, 255)
    
    # Paramètres d'affichage
    TILE_WIDTH = 64  # Largeur d'une tuile en pixels
    TILE_HEIGHT = 32 # Hauteur d'une tuile en pixels (ratio 2:1 pour iso classique)
    
    def __init__(self, map_instance: Map, width=1280, height=720, caption="MedievAIl Battle Simulator"):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16)
        
        self.map = map_instance
        
        # Caméra
        self.offset_x = width // 2
        self.offset_y = 100
        self.scroll_speed = 50
        
        # Chargement des assets (placeholders pour l'instant)
        self.assets = self._load_assets()

    def _load_assets(self):
        assets = {}
        
        def create_placeholder(color, width, height, shape="rect"):
            surf = pygame.Surface((width, height), pygame.SRCALPHA)
            if shape == "circle":
                pygame.draw.circle(surf, color, (width//2, height//2), min(width, height)//2)
            else:
                pygame.draw.rect(surf, color, (0, 0, width, height))
            return surf

        # Couleurs d'armées
        assets['unit_blue'] = create_placeholder((50, 50, 200), 20, 20, "circle")
        assets['unit_red'] = create_placeholder((200, 50, 50), 20, 20, "circle")
        
        # Obstacles
        assets['tree'] = create_placeholder((34, 139, 34), 20, 40, "rect") # Vert forêt
        assets['rock'] = create_placeholder((128, 128, 128), 30, 20, "rect") # Gris
        assets['water'] = create_placeholder((0, 191, 255), 64, 32, "rect") # Bleu eau
        
        # Sol (Tuile iso)
        tile = pygame.Surface((self.TILE_WIDTH, self.TILE_HEIGHT), pygame.SRCALPHA)
        pts = [
            (self.TILE_WIDTH//2, 0),
            (self.TILE_WIDTH, self.TILE_HEIGHT//2),
            (self.TILE_WIDTH//2, self.TILE_HEIGHT),
            (0, self.TILE_HEIGHT//2)
        ]
        pygame.draw.polygon(tile, (60, 100, 60), pts) # Herbe foncée
        pygame.draw.polygon(tile, (40, 80, 40), pts, 1) # Contour
        assets['tile'] = tile
        
        return assets

    def cart_to_iso(self, x, y):
        """
        convertit les coordonnées cartésiennes (grille logique) en coordonnées écran (isométriques).
        screen_x = (x - y) * (TILE_WIDTH / 2)
        screen_y = (x + y) * (TILE_HEIGHT / 2)
        """
        iso_x = (x - y) * (self.TILE_WIDTH / 2)
        iso_y = (x + y) * (self.TILE_HEIGHT / 2)
        return iso_x + self.offset_x, iso_y + self.offset_y

    def display(self, armies: list[Army], turn: int):
        """
        boucle de rendu principale appelée par l'engine.
        """
        # 1. Gestion des événements (Input)
        self._handle_events()
        
        # 2. Nettoyage écran
        self.screen.fill(self.COLOR_BG)
        
        # 3. Rendu de la Map (Sol)
        # dessine une graphe
        map_w, map_h = int(self.map.width), int(self.map.height)
        
        render_list = []

        for x in range(map_w):
            for y in range(map_h):
                sx, sy = self.cart_to_iso(x, y)
                # verification
                if -self.TILE_WIDTH < sx < self.screen.get_width() and -self.TILE_HEIGHT < sy < self.screen.get_height():
                    self.screen.blit(self.assets['tile'], (sx, sy))

        # B. Ajout des obstacles
        for type_name, x, y in self.map.obstacles:
            sx, sy = self.cart_to_iso(x, y)
            # On centre l'obstacle sur la tuile
            sprite_key = type_name.lower()
            if sprite_key in self.assets:
                img = self.assets[sprite_key]
                # Ajustement pour que le bas de l'image soit sur le centre de la tuile
                render_pos_x = sx + (self.TILE_WIDTH // 2) - (img.get_width() // 2)
                render_pos_y = sy + (self.TILE_HEIGHT // 2) - img.get_height()
                # On ajoute à la liste avec une clé de tri (y cartésien + x cartésien détermine la profondeur iso)
                depth = x + y
                render_list.append((depth, img, (render_pos_x, render_pos_y)))

        # C. Ajout des unités
        for army in armies:
            # Choix du sprite
            base_key = 'unit_blue' if army.army_id == 0 else 'unit_red'
            
            for unit in army.units:
                if not unit.is_alive:
                    continue
                
                sx, sy = self.cart_to_iso(unit.pos[0], unit.pos[1])
                img = self.assets[base_key]
                
                # Ici on pourrait dessiner une icone différente par dessus
                
                render_pos_x = sx + (self.TILE_WIDTH // 2) - (img.get_width() // 2)
                render_pos_y = sy + (self.TILE_HEIGHT // 2) - (img.get_height() // 2)
                
                # La profondeur est basée sur la position logique
                depth = unit.pos[0] + unit.pos[1]
                
                # Barre de vie au dessus de l'unité
                hp_ratio = unit.current_hp / unit.max_hp
                
                # On stocke une fonction lambda ou un objet pour dessiner l'unité + sa barre de vie
                render_list.append((depth, "unit", (img, render_pos_x, render_pos_y, hp_ratio)))

        # 4. Tri et Affichage des objets (Depth Sorting)
        # On trie par la clé 'depth' (x + y)
        render_list.sort(key=lambda x: x[0])
        
        for item in render_list:
            if item[1] == "unit":
                # Cas spécial unité avec barre de vie
                _, _, params = item
                img, rx, ry, hp = params
                self.screen.blit(img, (rx, ry))
                
                # Dessin barre de vie
                pygame.draw.rect(self.screen, (255, 0, 0), (rx, ry - 5, 20, 3))
                pygame.draw.rect(self.screen, (0, 255, 0), (rx, ry - 5, 20 * hp, 3))
            else:
                # Obstacle simple
                _, img, pos = item
                self.screen.blit(img, pos)

        # 5. Interface Utilisateur (HUD) (Req 12 & 14)
        self._draw_hud(armies, turn)
        
        # 6. Rafraîchissement
        pygame.display.flip()
        
        # Limite à 60 FPS pour ne pas brûler le CPU
        self.clock.tick(60)

    def _draw_hud(self, armies, turn):
        """Affiche les infos en surimpression."""
        # Fond semi-transparent en haut
        overlay = pygame.Surface((self.screen.get_width(), 40))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Texte Stats
        info_text = f"Tour: {turn} | FPS: {int(self.clock.get_fps())}"
        for i, army in enumerate(armies):
            alive = sum(1 for u in army.units if u.is_alive)
            info_text += f" | Armée {i}: {alive} unités"
            
        surf = self.font.render(info_text, True, self.COLOR_TEXT)
        self.screen.blit(surf, (10, 10))
        
        # Minimap (Req 11) - Coin bas droit
        mm_size = 150
        mm_x = self.screen.get_width() - mm_size - 10
        mm_y = self.screen.get_height() - mm_size - 10
        
        # Fond minimap
        pygame.draw.rect(self.screen, (0, 0, 0), (mm_x, mm_y, mm_size, mm_size))
        pygame.draw.rect(self.screen, (255, 255, 255), (mm_x, mm_y, mm_size, mm_size), 1)
        
        # Points sur la minimap
        scale_x = mm_size / self.map.width
        scale_y = mm_size / self.map.height
        
        for army in armies:
            color = (100, 100, 255) if army.army_id == 0 else (255, 100, 100)
            for unit in army.units:
                if unit.is_alive:
                    px = mm_x + int(unit.pos[0] * scale_x)
                    py = mm_y + int(unit.pos[1] * scale_y)
                    self.screen.set_at((px, py), color)

    def _handle_events(self):
        """Gestion des entrées clavier/souris. esc = exit, up down right left ou qszd pour controller le camera"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Scrolling continu
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.offset_x += self.scroll_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.offset_x -= self.scroll_speed
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            self.offset_y += self.scroll_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.offset_y -= self.scroll_speed
    