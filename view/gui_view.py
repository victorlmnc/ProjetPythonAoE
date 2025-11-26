# view/gui_view.py
import pygame
from core.army import Army
import os

# Définition des couleurs
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0) # Pour la barre de vie
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class PygameView:
    """
    Gère l'affichage de la bataille avec Pygame.
    """
    def __init__(self, map_instance, screen_size=(800, 600)):
        pygame.init()
        self.map = map_instance
        self.screen_size = screen_size
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("MedievAIl Battle GenerAIl")
        self.font = pygame.font.Font(None, 24)

        self.scale_x = self.screen_size[0] / self.map.width
        self.scale_y = self.screen_size[1] / self.map.height

        self.sprites = self._load_sprites()

    def _load_sprites(self):
        """Charge les sprites des unités depuis le dossier view/sprites."""
        sprites = {}
        sprite_dir = "view/sprites"
        if not os.path.isdir(sprite_dir):
            return sprites

        for filename in os.listdir(sprite_dir):
            unit_name = os.path.splitext(filename)[0]
            try:
                image = pygame.image.load(os.path.join(sprite_dir, filename)).convert_alpha()
                sprites[unit_name.lower()] = image
                print(f"Sprite chargé pour : {unit_name}")
            except pygame.error as e:
                print(f"Erreur lors du chargement du sprite {filename}: {e}")
        return sprites

    def _convert_pos(self, game_pos):
        """Convertit les coordonnées du jeu en coordonnées de l'écran."""
        screen_x = int(game_pos[0] * self.scale_x)
        screen_y = int(game_pos[1] * self.scale_y)
        return screen_x, screen_y

    def display(self, armies: list[Army], turn_count: int):
        """
        Dessine l'état actuel de la bataille.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self.screen.fill(WHITE)

        for army in armies:
            color = BLUE if army.army_id == 0 else RED
            for unit in army.units:
                if unit.is_alive:
                    pos = self._convert_pos(unit.pos)
                    radius = int(unit.hitbox_radius * self.scale_x)

                    unit_type_name = unit.__class__.__name__.lower()
                    if unit_type_name in self.sprites:
                        sprite = self.sprites[unit_type_name]
                        # Redimensionne le sprite et le dessine
                        scaled_sprite = pygame.transform.scale(sprite, (radius * 2, radius * 2))
                        self.screen.blit(scaled_sprite, (pos[0] - radius, pos[1] - radius))
                    else:
                        # Si pas de sprite, dessine un cercle
                        pygame.draw.circle(self.screen, color, pos, radius)

                    # Barre de vie
                    hp_percentage = unit.current_hp / unit.max_hp
                    hp_bar_width = radius * 2
                    hp_bar_height = 5
                    hp_bar_pos = (pos[0] - radius, pos[1] - radius - hp_bar_height - 2)

                    pygame.draw.rect(self.screen, BLACK, (*hp_bar_pos, hp_bar_width, hp_bar_height))
                    pygame.draw.rect(self.screen, GREEN, (*hp_bar_pos, int(hp_bar_width * hp_percentage), hp_bar_height))

        turn_text = self.font.render(f"Tour: {turn_count}", True, BLACK)
        self.screen.blit(turn_text, (10, 10))

        pygame.display.flip()
        pygame.time.delay(100)

    def __del__(self):
        """Nettoie Pygame à la fin."""
        pygame.quit()
