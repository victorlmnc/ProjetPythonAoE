# from map import SparseMap

# maptest = SparseMap(5, 5)
# print()
# print("map initialisée :")
# print(maptest)

# maptest.ajouter(1, 1, "K")
# maptest.ajouter(3, 2, "A")
# maptest.ajouter(4, 4, "P")

# print("map avec 3 unités :")
# print(maptest)

# maptest.deplacer(1, 1, 2, 1)
# print("Après déplacement du chevalier :")
# print(maptest)

# maptest.retirer(3, 2)
# print("Après retirer archer :")
# print(maptest)

# print("Case (2,1) :", maptest.obtenir(2, 1))
# print("Case (0,0) vide ?", maptest.est_vide(0, 0))
# print()

import math
import time
from map import SparseMap

class BattleEngine:
    """
    Moteur de simulation d'une bataille.
    Gère les déplacements, attaques et conditions de victoire.
    """

    def __init__(self, largeur, hauteur, armee_a, armee_b, general_a, general_b):
        """
        - armee_a / armee_b : listes d'unités (instances de Unite)
        - general_a / general_b : instances d’IA (objets avec decide_actions())
        """
        self.carte = SparseMap(largeur, hauteur)
        self.armee_a = armee_a
        self.armee_b = armee_b
        self.general_a = general_a
        self.general_b = general_b
        self.tour = 0
        self.en_cours = False

        # Placement initial : moitié gauche/droite
        self._placer_armees()

    # --------------------------
    # --- Placement initial ---
    # --------------------------
    def _placer_armees(self):
        """Place les unités des deux armées sur la carte."""
        for i, unite in enumerate(self.armee_a):
            x = i % (self.carte.largeur // 2)
            y = i // (self.carte.largeur // 2)
            self.carte.ajouter(x, y, unite)
            unite.position = (x, y)
            unite.proprietaire = "A"

        for i, unite in enumerate(self.armee_b):
            x = self.carte.largeur - 1 - (i % (self.carte.largeur // 2))
            y = i // (self.carte.largeur // 2)
            self.carte.ajouter(x, y, unite)
            unite.position = (x, y)
            unite.proprietaire = "B"

    # --------------------------
    # --- Boucle principale ---
    # --------------------------
    def run(self, max_tours=200):
        """Lance la simulation."""
        self.en_cours = True
        print("⚔️ Début de la bataille !")
        while self.en_cours and self.tour < max_tours:
            self.tour += 1
            print(f"\n--- Tour {self.tour} ---")

            # Tour de chaque général
            self._executer_tour(self.armee_a, self.armee_b, self.general_a)
            self._executer_tour(self.armee_b, self.armee_a, self.general_b)

            # Nettoyer les morts
            self.armee_a = [u for u in self.armee_a if u.hp > 0]
            self.armee_b = [u for u in self.armee_b if u.hp > 0]

            # Vérifier victoire
            if not self.armee_a or not self.armee_b:
                self._verifier_victoire()
                break
            
            time.sleep(0.3)

        print("🏁 Fin de la bataille.")

    # --------------------------
    # --- Exécution d’un tour ---
    # --------------------------
    def _executer_tour(self, armee, ennemis, general):
        """Fait agir chaque unité selon les ordres du général."""
        actions = general.decide_actions(armee, ennemis, self.carte)

        for action in actions:
            unite = action["unite"]
            if unite.hp <= 0:
                continue

            if action["type"] == "deplacement":
                x2, y2 = action["cible"]
                self.carte.deplacer(*unite.position, x2, y2)
                unite.position = (x2, y2)

            elif action["type"] == "attaque":
                cible = action["cible"]
                distance = self._distance(unite.position, cible.position)
                if distance <= max(1, unite.range):
                    unite.attaquer(cible)
                    if cible.hp <= 0:
                        self.carte.retirer(*cible.position)
                        ennemis.remove(cible)

    # --------------------------
    # --- Vérifications ---
    # --------------------------
    def _distance(self, pos1, pos2):
        """Distance euclidienne entre deux positions."""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def _verifier_victoire(self):
        """Renvoie True si une armée a gagné."""
        if not self.armee_a:
            print("🏆 Armée B victorieuse !")
            self.en_cours = False
            return True
        if not self.armee_b:
            print("🏆 Armée A victorieuse !")
            self.en_cours = False
            return True
        return False
