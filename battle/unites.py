import  pygame
import math


class Unit:
    def __init__(self, hp, attack, armor, pierce_armor, rng, line_of_sight,
                 speed, attacks, armours, image_path, position, team):
        self.hp = hp
        self.attack = attack
        self.armor = armor
        self.pierce_armor = pierce_armor
        self.range = rng
        self.line_of_sight = line_of_sight
        self.speed = speed
        self.attacks = attacks
        self.armours = armours
        self.position = list(position)
        self.team = team

        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (40, 40))
        except Exception as e:
            print(f"Erreur chargement image {image_path}: {e}")
            self.image = None

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.position)
        color = (255, 0, 0) if self.team == 1 else (0, 0, 255)
        pygame.draw.circle(screen, color, (int(self.position[0]+20), int(self.position[1]+20)), 5)

    def distance_to(self, other):
        dx = self.position[0] - other.position[0]
        dy = self.position[1] - other.position[1]
        return math.sqrt(dx**2 + dy**2)

    def get_target_armor(self, target, atk_type):
        melee_types = ["Base Melee", "Shock Infantry", "Mounted Units", "Camels"]
        ranged_types = ["Base Pierce", "All Archers", "Stone Defense & Harbors"]

        if atk_type in melee_types:
            return target.armor
        elif atk_type in ranged_types:
            return target.pierce_armor
        else:
            return target.armours.get(atk_type, 0)

    def attack_target(self, target):
        if self.distance_to(target) > self.range:
            return
        total_damage = 0
        for atk_type, dmg in self.attacks.items():
            armor = self.get_target_armor(target, atk_type)
            damage = max(0, dmg - armor)
            total_damage += damage
        total_damage = max(1, total_damage)
        target.hp -= total_damage

    def dead(self):
        return self.hp <= 0

    def move_towards(self, target):
        dx = target.position[0] - self.position[0]
        dy = target.position[1] - self.position[1]
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            self.position[0] += self.speed * dx / dist
            self.position[1] += self.speed * dy / dist

# --- Classes enfants ---
class Infantry(Unit): pass
class Cavalry(Unit): pass
class Archer(Unit): pass

# --- Classes spécifiques avec stats originales ---
class LongSwordsman(Infantry):
    def __init__(self, position=(0,0), team=1):
        super().__init__(
            hp=60,
            attack=9,
            armor=1,
            pierce_armor=1,
            rng=0,
            line_of_sight=4,
            speed=1.0,
            attacks={
                "Shock Infantry": 6,
                "Standard Buildings": 3,
                "Base Melee": 9,
                "Mounted Units": 0,
                "Camels": 0,
                "All Archers": 0
            },
            armours={
                "Infantry": 0,
                "Base Melee": 1,
                "Base Pierce": 1,
                "Obsolete": 0
            },
            image_path="images/long_swordsman.WEBP",
            position=position,
            team=team
        )

class Pikeman(Infantry):
    def __init__(self, position=(0,0), team=1):
        super().__init__(
            hp=55, attack=7, armor=0, pierce_armor=0, rng=0, line_of_sight=4,
            speed=1.2,
            attacks={"Shock Infantry": 1, "Standard Buildings": 1, "Elephants": 25,
                     "Base Melee": 4, "Mounted Units": 22, "Ships": 16, "Camels": 18,
                     "Mamelukes": 7, "Fishing Ships": 16, "All Archers": 0},
            armours={"Spear Units": 0, "Infantry": 0, "Base Melee": 0, "Base Pierce": 0, "Obsolete": 0},
            image_path="images/pikeman.WEBP",
            position=position,
            team=team
        )

class Knight(Cavalry):
    def __init__(self, position=(0,0), team=1):
        super().__init__(
            hp=100, attack=10, armor=2, pierce_armor=2, rng=0, line_of_sight=4,
            speed=1.35,
            attacks={"Base Melee": 10, "All Archers": 0, "All Buildings": 0,
                     "Standard Buildings": 0, "Skirmishers": 0, "Cavalry Resistance": -3,
                     "Siege Units": 0, "Obsolete": 0},
            armours={"Base Melee": 2, "Mounted Units": 0, "Base Pierce": 2, "Obsolete": 0},
            image_path="images/knight.WEBP",
            position=position,
            team=team
        )

class Crossbowman(Archer):
    def __init__(self, position=(0,0), team=1):
        super().__init__(
            hp=35,
            attack=5,
            armor=0,
            pierce_armor=0,
            rng=5,
            line_of_sight=7,
            speed=0.96,
            attacks={
                "Spear Units": 3,
                "Standard Buildings": 0,
                "Base Pierce": 5,
                "High Pierce Armor Siege Units": 0,
                "Stone Defense & Harbors": 0
            },
            armours={
                "Base Melee": 0,
                "All Archers": 0,
                "Base Pierce": 0,
                "Obsolete": 0
            },
            image_path="images/crossbowman.WEBP",
            position=position,
            team=team
        )
