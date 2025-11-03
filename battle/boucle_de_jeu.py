from map import SparseMap

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