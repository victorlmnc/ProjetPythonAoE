from map import SparseMap
from unites import Unite
import msvcrt
from time import sleep
import random

class Game :
    def __init__(self, map, vitesse=1.0) : 
        self.map = map
        self.etat = "terminé" # "running" ou "pause" ou "terminé"
        self.horloge = 0

    def input_clavier(self) : # pour mettre pause, play ou changer de vitesse avec touches clavier
        if msvcrt.kbhit() :
            touche_clavier = msvcrt.getch().lower
            if touche_clavier == "p" :
                if self.etat == "running" :
                    self.etat = "pause"
                    print("--- Jeu en Pause ---")
                elif self.etat == "pause" :
                    self.etat = "running"
                    print("--- Jeu repris ---")
                elif self.etat == "terminé" :
                    self.etat = "running"
                    print("--- Jeu commencé ---")

            elif touche_clavier == "q" :
                self.etat = "terminé"
                print("--- Fin de la partie ---")

    def update(self) : # maj unites, deplacements, mort..., verifie victoire, augmente l'horloge
        self.horloge += 1

        if self.map.grille :
        # On choisit une unité au hasard
            (x, y), obj = random.choice(list(self.map.grille.items()))

            direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            dx, dy = direction

            # Calcul de la nouvelle position
            new_x = (x + dx) % self.map.largeur
            new_y = (y + dy) % self.map.hauteur

            # On vérifie que la case d'arrivée est vide
            if self.map.est_vide(new_x, new_y):
                self.map.retirer(x, y)
                self.map.ajouter(new_x, new_y, obj)
                print(f"L’unité '{obj}' s’est déplacée de {(x, y)} vers {(new_x, new_y)}")

        else:
            print("Map vide, aucune unité à déplacer.")

        # toutes les 5 itérations : on enlève un symbole au hasard
        if self.horloge % 5 == 0 and self.map.grille:
            cible = random.choice(list(self.map.grille.keys()))
            self.map.retirer(*cible)

        # fin auto après 60 ticks pour la démo
        if self.horloge >= 60:
            print("== Fin automatique de la démo ==")
            self.etat = "terminé"
    
    def sauvegarder(self, filename) :
        pass

    def charger(self, filename) :
        pass

    def run(self) :
        print("--- Début de la partie ---")
        self.etat = "running"
        print(self.map)

        while self.etat != "terminé" :
            print("Horloge : ", self.horloge)
            sleep(0.5)

            self.input_clavier()

            if self.etat == "running" :
                    self.update()
                    print(self.map)

            if self.etat == "terminé" :
                break

        print("--- Fin de la partie ---")

if __name__ == "__main__":
    game_map = SparseMap(10, 10)

    game_map.ajouter(1, 1, "K")   # Chevalier
    game_map.ajouter(2, 1, "A")   # Archer
    game_map.ajouter(3, 1, "P")   # Paysan
    game_map.ajouter(1, 2, "S")   # Soldat
    game_map.ajouter(2, 2, "L")   # Lancier
    game_map.ajouter(3, 2, "C")   # Cavalier

    # Armée du joueur 2
    game_map.ajouter(8, 8, "k")   # Chevalier adverse
    game_map.ajouter(7, 8, "a")   # Archer adverse
    game_map.ajouter(8, 7, "p")   # Paysan adverse
    game_map.ajouter(7, 7, "s")   # Soldat adverse
    game_map.ajouter(9, 7, "c")   # Cavalier adverse
    game = Game(game_map)
    game.run()