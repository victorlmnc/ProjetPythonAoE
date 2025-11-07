
from unites import Unite

def calculate_damage(attacker: Unite, defender: Unite, elevation_factor: float = 1.0) -> int:
    # choose armor type
    if getattr(attacker, "range", 0) > 0:
        effective_armor = defender.pierce_armor
    else:
        effective_armor = defender.armor

    # calculate all types of dmg
    damage_components = [attacker.attack]
    for unit_type, bonus_damage in getattr(attacker, "bonus_vs", {}).items():
        # If the unit matches, apply the bonus
        if defender.type_unite == unit_type or defender.nom == unit_type:
            damage_components.append(bonus_damage)
    
    # raw dmg
    raw_damage = 0
    for attack_value in damage_components:
        raw_damage += max(0, attack_value - effective_armor)
    
    # dmg >=1
    total_damage = elevation_factor * raw_damage
    final_damage = max(1, int(total_damage))
    return final_damage

def perform_attack(attacker: Unite, defender: Unite, elevation_factor: float = 1.0) -> int:
    damage = calculate_damage(attacker, defender, elevation_factor)
    defender.hp = max(0, defender.hp - damage)
    return damage
