class Unite:
    """Classe de base représentant une unité militaire du jeu."""
    def __init__(self, nom, type_unite, hp, attack, armor, pierce_armor, speed, range_):
        self.nom = nom
        self.type_unite = type_unite
        self.hp = hp
        self.attack = attack
        self.armor = armor
        self.pierce_armor = pierce_armor
        self.speed = speed
        self.range = range_
        self.bonus_vs = {}  # bonus contextuels (ex: Pikeman vs Cavalerie)

    # --- Formule officielle d’Age of Empires II ---
    def calcul_degats(self, cible, elevation_factor=1.0):
        """
        Damage = max(1, k_elev * Σ_i max(0, Attack_i - Armor_i))
        """
        # Type d’armure (mêlée ou perforante)
        armor = cible.pierce_armor if self.range > 0 else cible.armor

        # Base + bonus selon le type de la cible
        attacks = [self.attack]
        attacks += [bonus for unit_type, bonus in self.bonus_vs.items()
                    if cible.type_unite == unit_type or cible.nom == unit_type]

        # Application directe de la formule
        raw_damage = sum(max(0, atk - armor) for atk in attacks)
        total_damage = max(1, elevation_factor * raw_damage)

        return int(total_damage)

    def subir_degats(self, montant):
        self.hp -= max(0, montant)
        if self.hp < 0:
            self.hp = 0

    def attaquer(self, cible, elevation_factor=1.0):
        degats = self.calcul_degats(cible, elevation_factor)
        cible.subir_degats(degats)
        print(f"{self.nom} attaque {cible.nom} et inflige {degats} dégâts !")
        if cible.hp <= 0:
            print(f"💀 {cible.nom} est éliminé !")


# --------------------------------------------------------------------
# 🛡️ INFANTERIE DE BASE
# --------------------------------------------------------------------
class Infantry(Unite):
    def __init__(self):
        super().__init__(
            "Infantry", "Infanterie",
            hp=40, attack=4, armor=0, pierce_armor=1,
            speed=0.9, range_=0
        )
        self.line_of_sight = 4
        self.reload_time = 2
        self.build_time = 21
        self.cost = {"food": 50, "gold": 20}
        self.bonus_vs = {}  # pas de bonus spécifiques


# --------------------------------------------------------------------
# 🏹 ARCHER
# --------------------------------------------------------------------
class Archer(Unite):
    def __init__(self):
        super().__init__(
            "Archer", "Archer",
            hp=30, attack=4, armor=0, pierce_armor=0,
            speed=0.96, range_=4
        )
        self.line_of_sight = 6
        self.reload_time = 2
        self.attack_delay = 0.35
        self.build_time = 35
        self.accuracy = 0.8
        self.cost = {"wood": 25, "gold": 45}
        self.bonus_vs = {"Infanterie": 2}  # Bonus structurel AoE2

    def calcul_degats(self, cible, elevation_factor=1.0):
        import random
        if random.random() > self.accuracy:
            print(f"{self.nom} rate son tir sur {cible.nom} !")
            return 0
        return super().calcul_degats(cible, elevation_factor)


# --------------------------------------------------------------------
# 🪓 PIQUIER
# --------------------------------------------------------------------
class Pikeman(Unite):
    def __init__(self):
        super().__init__(
            "Pikeman", "Infanterie",
            hp=55, attack=4, armor=0, pierce_armor=0,
            speed=1.0, range_=0
        )
        self.line_of_sight = 4
        self.reload_time = 3
        self.build_time = 22
        self.cost = {"food": 35, "wood": 25}
        # Bonus officiels AoE2
        self.bonus_vs = {
            "Cavalerie": 22,
            "Elephant": 25,
            "Camel": 18,
            "Ship": 16,
            "Fishing Ship": 16,
        }


# --------------------------------------------------------------------
# 🏹 TIRAILLEUR (SKIRMISHER)
# --------------------------------------------------------------------
class Skirmisher(Unite):
    def __init__(self):
        super().__init__(
            "Skirmisher", "Archer",
            hp=30, attack=2, armor=0, pierce_armor=3,
            speed=0.96, range_=4
        )
        self.min_range = 1
        self.line_of_sight = 6
        self.reload_time = 3
        self.attack_delay = 0.51
        self.build_time = 26
        self.accuracy = 0.9
        self.cost = {"food": 25, "gold": 35}
        self.bonus_vs = {"Archer": 4, "Pikeman": 1}

    def calcul_degats(self, cible, elevation_factor=1.0):
        import random
        distance = getattr(cible, "distance", 2)
        if distance < self.min_range:
            print(f"{self.nom} ne peut pas tirer à bout portant sur {cible.nom} !")
            return 0
        if random.random() > self.accuracy:
            print(f"{self.nom} rate son tir sur {cible.nom} !")
            return 0
        return super().calcul_degats(cible, elevation_factor)


# --------------------------------------------------------------------
# 🐎 CHEVALIER
# --------------------------------------------------------------------
class Knight(Unite):
    def __init__(self):
        super().__init__(
            "Knight", "Cavalerie",
            hp=100, attack=10, armor=2, pierce_armor=2,
            speed=1.35, range_=0
        )
        self.line_of_sight = 4
        self.reload_time = 1.8
        self.attack_delay = 0.67
        self.build_time = 30
        self.cost = {"food": 60, "gold": 75}
        self.bonus_vs = {}  # pas de bonus spécifiques
class Cavalry(Unite):
    def __init__(self):
        super().__init__(
            "Scout Cavalry", "Light Cavalry",
            hp=45, attack=3, armor=0, pierce_armor=2,
            speed=1.2, range_=0
        )
        self.line_of_sight = 4
        self.reload_time = 2
        self.attack_delay = 0.6
        self.build_time = 30
        self.accuracy = 1.0  # Suppose attaque toujours réussie sauf exceptions
        self.cost = {"food": 80}
        self.bonus_vs = {"Monastery Units": 5}  # Fort contre les unités monastiques
        self.weak_vs = {"Spearman": 5, "Camel Riders": 5}  # Faible contre ces unités
        self.upgrades = {
            "Blacksmith": ["attack", "armor"],
            "Stable": ["speed", "hp", "to Light Cavalry"],
            "Castle": ["creation_speed"],
            "Monastery": ["resistance_to_conversion"]
        }

    def calcul_degats(self, cible, elevation_factor=1.0):
        import random
        distance = getattr(cible, "distance", 1)
        if distance > 1:
            print(f"{self.nom} attaque au corps à corps {cible.nom} !")
        return super().calcul_degats(cible, elevation_factor)
