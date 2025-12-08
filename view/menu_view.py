import pygame
import os
from core.definitions import GENERAL_CLASS_MAP, UNIT_CLASS_MAP

# Colors
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (50, 50, 200)
BUTTON_HOVER_COLOR = (70, 70, 220)
BUTTON_TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (200, 50, 50)
HEADER_COLOR = (100, 100, 100)

class Button:
    def __init__(self, x, y, w, h, text, action=None, param=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.param = param
        self.is_hovered = False

    def draw(self, screen, font):
        color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=5)
        
        txt_surf = font.render(self.text, True, BUTTON_TEXT_COLOR)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, txt_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.action:
                return self.action(self.param)
        return None

class MenuView:
    def __init__(self):
        pygame.init()
        self.width = 1280
        self.height = 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("MedievAIl - Advanced Battle Setup")
        self.font = pygame.font.SysFont('Arial', 20, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 40, bold=True)
        self.clock = pygame.time.Clock()

        # Data
        self.generals = list(GENERAL_CLASS_MAP.keys())
        self.unit_types = list(UNIT_CLASS_MAP.keys())
        
        # Load maps
        self.maps = []
        try:
            if os.path.exists("maps"):
                for f in os.listdir("maps"):
                    if f.endswith(".map"):
                        self.maps.append(os.path.join("maps", f))
        except FileNotFoundError:
            pass
        
        if not self.maps:
            self.maps = ["maps/small.map"] # Fallback
        self.maps.sort()

        # State
        self.map_idx = 0
        self.gen1_idx = 0
        self.gen2_idx = 1 if len(self.generals) > 1 else 0
        
        # Army Compositions: { 'Archer': 10, 'Knight': 5 ... }
        self.army1_comp = {u: 0 for u in self.unit_types}
        self.army2_comp = {u: 0 for u in self.unit_types}
        
        # Defaults
        if self.unit_types:
            self.army1_comp[self.unit_types[0]] = 10
            self.army2_comp[self.unit_types[0]] = 10

        self.running = True
        self.start_game = False
        self.buttons = []
        self._create_ui()

    def _create_ui(self):
        self.buttons = []
        cx = self.width // 2
        
        # --- Map Selector (Top Center) ---
        self.buttons.append(Button(cx - 200, 100, 40, 40, "<", self._change_map, -1))
        self.buttons.append(Button(cx + 160, 100, 40, 40, ">", self._change_map, 1))

        # --- Columns Setup ---
        col1_x = self.width // 4
        col2_x = 3 * self.width // 4
        start_y = 180
        
        # --- General Selectors ---
        # Army 1 General
        self.buttons.append(Button(col1_x - 130, start_y, 40, 40, "<", self._change_gen, (1, -1)))
        self.buttons.append(Button(col1_x + 90, start_y, 40, 40, ">", self._change_gen, (1, 1)))
        
        # Army 2 General
        self.buttons.append(Button(col2_x - 130, start_y, 40, 40, "<", self._change_gen, (2, -1)))
        self.buttons.append(Button(col2_x + 90, start_y, 40, 40, ">", self._change_gen, (2, 1)))

        # --- Unit Counts (Rows) ---
        row_start_y = 260
        row_height = 50
        
        for i, u_type in enumerate(self.unit_types):
            y = row_start_y + i * row_height
            
            # Army 1 Unit Controls
            self.buttons.append(Button(col1_x - 80, y, 30, 30, "-", self._change_unit_count, (1, u_type, -1)))
            self.buttons.append(Button(col1_x + 50, y, 30, 30, "+", self._change_unit_count, (1, u_type, 1)))

            # Army 2 Unit Controls
            self.buttons.append(Button(col2_x - 80, y, 30, 30, "-", self._change_unit_count, (2, u_type, -1)))
            self.buttons.append(Button(col2_x + 50, y, 30, 30, "+", self._change_unit_count, (2, u_type, 1)))

        # --- Start Button ---
        self.buttons.append(Button(cx - 100, self.height - 80, 200, 60, "START BATTLE", self._start))

    def _change_map(self, direction):
        self.map_idx = (self.map_idx + direction) % len(self.maps)

    def _change_gen(self, params):
        army_num, direction = params
        if army_num == 1:
            self.gen1_idx = (self.gen1_idx + direction) % len(self.generals)
        else:
            self.gen2_idx = (self.gen2_idx + direction) % len(self.generals)

    def _change_unit_count(self, params):
        army_num, u_type, direction = params
        target_dict = self.army1_comp if army_num == 1 else self.army2_comp
        
        step = 1
        if pygame.key.get_pressed()[pygame.K_LSHIFT]: step = 5
        if pygame.key.get_pressed()[pygame.K_LCTRL]: step = 10
        
        target_dict[u_type] = max(0, min(200, target_dict[u_type] + direction * step))

    def _start(self, _):
        # Ensure at least one unit per side?
        count1 = sum(self.army1_comp.values())
        count2 = sum(self.army2_comp.values())
        
        if count1 > 0 and count2 > 0:
            self.start_game = True
            self.running = False
        else:
            print("Cannot start: Armies must have at least 1 unit.")

    def run(self):
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                for btn in self.buttons:
                    btn.handle_event(event)

            self.screen.fill(BG_COLOR)
            
            # --- Title ---
            title = self.title_font.render("Battle Configuration", True, TEXT_COLOR)
            self.screen.blit(title, (self.width//2 - title.get_width()//2, 20))

            cx = self.width // 2
            col1_x = self.width // 4
            col2_x = 3 * self.width // 4

            # --- Map Section ---
            map_name = os.path.basename(self.maps[self.map_idx])
            lbl_map = self.font.render("Selected Map:", True, TEXT_COLOR)
            val_map = self.font.render(map_name, True, ACCENT_COLOR)
            self.screen.blit(lbl_map, (cx - 190 - lbl_map.get_width(), 110))
            self.screen.blit(val_map, (cx - val_map.get_width()//2, 110))

            # --- Column Headers ---
            # Draw vertical separator
            pygame.draw.line(self.screen, HEADER_COLOR, (cx, 160), (cx, self.height - 100), 2)
            head1 = self.title_font.render("ARMY 1 (Blue)", True, (100, 100, 255))
            head2 = self.title_font.render("ARMY 2 (Red)", True, (255, 100, 100))
            self.screen.blit(head1, (col1_x - head1.get_width()//2, 140))
            self.screen.blit(head2, (col2_x - head2.get_width()//2, 140))

            start_y = 180
            
            # --- General Display ---
            gen1_name = self.generals[self.gen1_idx]
            gen2_name = self.generals[self.gen2_idx]
            
            g_lbl1 = self.font.render(gen1_name, True, TEXT_COLOR)
            g_lbl2 = self.font.render(gen2_name, True, TEXT_COLOR)
            
            self.screen.blit(g_lbl1, (col1_x - g_lbl1.get_width()//2, start_y + 10))
            self.screen.blit(g_lbl2, (col2_x - g_lbl2.get_width()//2, start_y + 10))

            # --- Unit Rows ---
            row_start_y = 260
            row_height = 50
            
            for i, u_type in enumerate(self.unit_types):
                y = row_start_y + i * row_height
                
                # Label (Center of column)
                u_lbl = self.font.render(u_type, True, (200, 200, 200))
                
                # Col 1
                self.screen.blit(u_lbl, (col1_x - 120 - u_lbl.get_width(), y + 5))
                count1 = self.army1_comp[u_type]
                c1_surf = self.font.render(str(count1), True, ACCENT_COLOR if count1 > 0 else (100,100,100))
                self.screen.blit(c1_surf, (col1_x - c1_surf.get_width()//2, y + 5))

                # Col 2
                self.screen.blit(u_lbl, (col2_x - 120 - u_lbl.get_width(), y + 5))
                count2 = self.army2_comp[u_type]
                c2_surf = self.font.render(str(count2), True, ACCENT_COLOR if count2 > 0 else (100,100,100))
                self.screen.blit(c2_surf, (col2_x - c2_surf.get_width()//2, y + 5))

            # --- Total Count Summary ---
            sum1 = sum(self.army1_comp.values())
            sum2 = sum(self.army2_comp.values())
            
            sum1_txt = self.font.render(f"Total: {sum1}", True, TEXT_COLOR)
            sum2_txt = self.font.render(f"Total: {sum2}", True, TEXT_COLOR)
            
            self.screen.blit(sum1_txt, (col1_x - sum1_txt.get_width()//2, self.height - 140))
            self.screen.blit(sum2_txt, (col2_x - sum2_txt.get_width()//2, self.height - 140))

            # --- Draw Buttons ---
            for btn in self.buttons:
                btn.check_hover(mouse_pos)
                btn.draw(self.screen, self.font)

            pygame.display.flip()
            self.clock.tick(30)

        if self.start_game:
            return {
                "map": self.maps[self.map_idx],
                "general1": self.generals[self.gen1_idx],
                "general2": self.generals[self.gen2_idx],
                "comp1": self.army1_comp,
                "comp2": self.army2_comp
            }
        return None