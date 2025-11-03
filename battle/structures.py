import math

class Building:

    #Base class for buildings (add castle later, attack and reload is for castle)

    def __init__(self, owner, name, max_hp, size, attack, attack_range, reload_time):
        self.owner = owner
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.size = size
        self.x = 0
        self.y = 0
        self.center_x = 0
        self.center_y = 0
        self.attack = attack
        self.attack_range = attack_range
        self.reload_time = reload_time
        self.current_reload = 0.0
        self.target = None
        self.unit_type = "Building"
        self.melee_armor = 8
        self.pierce_armor = 8

    def set_position(self, x, y):
        #Set the position and calculate the center coordinates
        self.x = x
        self.y = y
        self.center_x = x + self.size[0] / 2
        self.center_y = y + self.size[1] / 2

    @property
    def is_alive(self):
        return self.hp > 0

    def distance_to(self, unit):
        dx = self.center_x - unit.x
        dy = self.center_y - unit.y
        return math.sqrt(dx * dx + dy * dy)

    def take_damage(self, amount):
        #Take damage
        if self.hp > 0:
            self.hp -= amount
            if self.hp <= 0:
                self.hp = 0
                print(f"{self.name} belonging to {self.owner.name} has been destroyed!")

    def find_target(self, enemy_units):
        #Find an enemy within attack range.
        for enemy in enemy_units:
            if enemy.is_alive:
                dist = self.distance_to(enemy)
                if dist <= self.attack_range:
                    return enemy
        return None

    def update(self, enemy_units, tick_duration_seconds):
        #Update logic for buildings (castle)
        if not self.is_alive or self.attack == 0:
            return
        if self.current_reload > 0:
            self.current_reload -= tick_duration_seconds
            return
        if self.target:
            if not self.target.is_alive or self.distance_to(self.target) > self.attack_range:
                self.target = None
        if not self.target:
            self.target = self.find_target(enemy_units)
        if self.target:
            damage = self.attack - self.target.pierce_armor
            self.target.take_damage(max(1, damage))
            self.current_reload = self.reload_time


class Wonder(Building):
    #Wonder - victory condition structure.
    def __init__(self, owner):
        super().__init__(
            owner=owner,
            name="Wonder",
            max_hp=4800,
            size=(4, 4),
            attack=0,
            attack_range=0,
            reload_time=999
        )
        self.unit_type = "Wonder"


class Player:
    def __init__(self, name):
        self.name = name
