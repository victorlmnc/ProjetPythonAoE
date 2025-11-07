
from unites import Unite
from structures import Building

def calculate_damage(attacker: Unite, target, elevation_factor: float = 1.0) -> int:
    is_ranged = getattr(attacker, "range", 0) > 0
    # choose armor type
    if isinstance(target, Building):
        armor = target.pierce_armor if is_ranged else target.melee_armor
        target_type = target.unit_type
        target_name = target.name
    else:
        armor = target.pierce_armor if is_ranged else target.armor
        target_type = target.type_unite
        target_name = target.nom
    # calculate all types of dmg
    attacks = [attacker.attack]
    for unit_type, bonus in getattr(attacker, "bonus_vs", {}).items():
        if target_type == unit_type or target_name == unit_type:
            attacks.append(bonus)

    # dmg formula
    raw_damage = sum(max(0, atk - armor) for atk in attacks)
    total_damage = max(1, int(elevation_factor * raw_damage))
    return total_damage

    #deal dmg
def perform_attack(attacker: Unite, target, elevation_factor: float = 1.0) -> int:
    damage = calculate_damage(attacker, target, elevation_factor)
    if isinstance(target, Building):
        target.take_damage(damage)
    else:
        target.hp = max(0, target.hp - damage)
    return damage
