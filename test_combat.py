# test_combat.py
from core.unit import Knight, Pikeman

print("--- Début de la simulation de combat simple ---")

# Création des unités
knight = Knight(unit_id=1, army_id=0, pos=(0, 0))
pikeman = Pikeman(unit_id=2, army_id=1, pos=(1, 0)) # Juste à côté

print(f"État initial: {knight} vs {pikeman}")

# Le chevalier attaque le piquier
knight.attack(pikeman)

print(f"État après 1 attaque: {knight} vs {pikeman}")

# Combat à mort
while knight.is_alive and pikeman.is_alive:
    print("\n--- Nouveau tour ---")
    if knight.is_alive:
        knight.attack(pikeman)
    if pikeman.is_alive:
        pikeman.attack(knight)
    print(f"État: {knight} vs {pikeman}")

print(f"\n--- Fin du combat ---")
winner = "Chevalier" if knight.is_alive else "Piquier"
print(f"Le vainqueur est: {winner}")