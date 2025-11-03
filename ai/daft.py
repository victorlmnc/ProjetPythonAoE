import math

class MajorDAFT:
    def decide_actions(self, armee, ennemis, carte):
        actions = []
        for unite in armee:
            if unite.hp <= 0:
                continue
            if not ennemis:
                break

            # Trouver l'ennemi le plus proche
            cible = min(ennemis, key=lambda e: self._distance(unite, e))
            actions.append({"unite": unite, "type": "attaque", "cible": cible})
        return actions

    def _distance(self, u1, u2):
        (x1, y1), (x2, y2) = u1.position, u2.position
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
