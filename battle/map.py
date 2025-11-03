class SparseMap:
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.grille = {}  # dictionnaire {(x,y): contenu}

    def ajouter(self, x, y, obj):
        """Ajoute une unité ou un bâtiment à la position donnée"""
        if 0 <= x < self.largeur and 0 <= y < self.hauteur:
            self.grille[(x, y)] = obj
        else:
            raise ValueError("Position en dehors de la carte")

    def retirer(self, x, y):
        """Supprime ce qu’il y a à une position"""
        if (x, y) in self.grille:
            del self.grille[(x, y)]

    def deplacer(self, x1, y1, x2, y2):
        """Déplace une unité de (x1,y1) vers (x2,y2)"""
        if (x1, y1) not in self.grille:
            raise ValueError("Pas d’unité à déplacer")
        if not (0 <= x2 < self.largeur and 0 <= y2 < self.hauteur):
            raise ValueError("Nouvelle position invalide")
        
        self.grille[(x2, y2)] = self.grille.pop((x1, y1))

    def obtenir(self, x, y):
        """Retourne ce qu’il y a à une position (None si vide)"""
        return self.grille.get((x, y), None)

    def est_vide(self, x, y):
        """Vérifie si une case est vide"""
        return (x, y) not in self.grille

    def __str__(self):
        """Affichage rapide en mode texte"""
        s = ""
        for y in range(self.hauteur):
            for x in range(self.largeur):
                s += "." if (x, y) not in self.grille else str(self.grille[(x, y)])[0]
            s += "\n"
        return s