from map import SparseMap
from unites import Unite
class Game :
    def __init__(self, map, unites, vitesse=1.0) : 
        self.map = map
        self.unites = unites #liste des unites
        self.etat = "running" # "running" ou "pause" ou "terminé"
        self.horloge = 0

    def input_clavier(self) : # pour mettre pause, play ou changer de vitesse avec touches clavier
        pass

    def update(self, vitesse=1.0) : # maj unites, deplacements, mort..., verifie victoire, augmente l'horloge
        pass
    
    def sauvegarder(self, filename) :
        pass

    def charger(self, filename) :
        pass

    def run(self) :
        while self.etat != "terminé" :
            if self.etat == "running" :
                    self.update()
                    print(self.map)

maptest = SparseMap(5, 5)
print()
print("map initialisée :")
print(maptest)

maptest.ajouter(1, 1, "K")
maptest.ajouter(3, 2, "A")
maptest.ajouter(4, 4, "P")

print("map avec 3 unités :")
print(maptest)

maptest.deplacer(1, 1, 2, 1)
print("Après déplacement du chevalier :")
print(maptest)

maptest.retirer(3, 2)
print("Après retirer archer :")
print(maptest)

print("Case (2,1) :", maptest.obtenir(2, 1))
print("Case (0,0) vide ?", maptest.est_vide(0, 0))
print()