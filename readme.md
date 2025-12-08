# Projet de programmation : MedievAIl BAIttle GenerAIl

Ce projet est un simulateur de batailles médiévales inspiré d'Age of Empires II, axé sur les tactiques militaires IA sans aucun aspect économique.

## Comment utiliser le simulateur

Le programme utilise une interface en ligne de commande. Toutes les commandes commencent par `python main.py`, suivi d'une sous-commande (`battle`, `tournament`, `lanchester`) et de ses options.

### 1. Lancer une bataille simple

Pour lancer une simulation de bataille, utilisez la commande `battle`.

#### Vue Terminal (par défaut)
Vous verrez une représentation textuelle de la bataille directement dans votre terminal.

```bash
python main.py battle --map "maps/small.map" --army1 "armies/armee_test_bleue.txt" --army2 "armies/armee_test_rouge.txt"
```

#### Vue Graphique (Pygame)
Pour une expérience visuelle, vous pouvez utiliser la vue Pygame.

**Prérequis :** Assurez-vous d'avoir installé la bibliothèque Pygame.
```bash
pip install pygame
```

**Commande :**
Ajoutez l'option `--view pygame` pour ouvrir une fenêtre graphique qui affichera la bataille.
```bash
python main.py battle --map "maps/small.map" --army1 "armies/armee_test_bleue.txt" --army2 "armies/armee_test_rouge.txt" --view pygame
```

### 2. Lancer un tournoi automatique

Pour faire s'affronter plusieurs IA sur différentes cartes et obtenir un tableau de scores, utilisez la commande `tournament`. Ce mode est "headless" (sans affichage) pour garantir une exécution rapide.

```bash
python main.py tournament --generals CaptainBRAINDEAD MajorDAFT --maps maps/small.map --armies armies/armee_test_bleue.txt armies/armee_test_rouge.txt
```

### 3. Tester les lois de Lanchester

Pour lancer un scénario généré de manière procédurale basé sur les lois de Lanchester (une petite armée contre une armée deux fois plus grande), utilisez la commande `lanchester`.

```bash
python main.py lanchester --unit Knight --n 10 --map maps/small.map
```
Vous pouvez également lancer ce scénario avec la vue Pygame :
```bash
python main.py lanchester --unit Knight --n 10 --map maps/small.map --view pygame
```

### 4. Sauvegarder et charger une partie

Vous pouvez sauvegarder l'état d'une bataille à la fin de la simulation et le recharger plus tard.

*   **Pour sauvegarder :** Ajoutez l'option `--save_path`.
    ```bash
    python main.py battle --map "maps/small.map" --army1 "armies/armee_test_bleue.txt" --army2 "armies/armee_test_rouge.txt" --max_turns 10 --save_path saves/partie_sauvegardee.sav
    ```

*   **Pour charger :** Utilisez l'option `--load_game` avec la commande `battle`.
    ```bash
    python main.py battle --load_game saves/partie_sauvegardee.sav --max_turns 20
    ```

### 5. menu pour choisir troupes et IA :
```bash
python main.py gui
```

## La carte : au cœur de la simulation

La carte (ou *Map*) est l’élément central qui représente le champ de bataille. Elle a été conçue pour être à la fois robuste, performante et flexible, conformément aux exigences du projet.

### 1. Une grille 2D robuste et performante

La carte est une grille 2D de `tuiles` (*tiles*).
- **Dimensions minimales :** 120x120, conformément aux plus petites cartes d'Age of Empires II.
- **Performance :** La structure de données sous-jacente (une liste de listes en Python) garantit un accès en O(1) à n'importe quelle tuile, ce qui est crucial pour les simulations rapides et les tournois "headless".

### 2. Anatomie d’une tuile

Chaque tuile de la carte est un objet qui contient les informations suivantes :
- **Élévation :** Un entier de 0 à 16.
- **Type de terrain :** Une chaîne de caractères (ex: `"plain"`, `"forest"`). Actuellement, seul `"plain"` est utilisé, mais la structure est prête pour des extensions.
- **Passabilité :** Une propriété implicite. Si une tuile contient un obstacle ou un bâtiment, elle devient non-traversable.
- **Unités présentes :** Une liste des unités actuellement situées sur cette tuile.

### 3. Gestion des positions : flottantes vs. grille

Le simulateur utilise un système hybride :
- **Unités :** Leurs positions sont stockées en coordonnées **flottantes** (ex: `(50.3, 75.8)`) pour permettre des mouvements fluides et précis.
- **Carte :** La carte utilise des coordonnées **entières** pour accéder aux tuiles (ex: `(50, 75)`).

La conversion se fait simplement en tronquant les coordonnées flottantes. Par exemple, une unité à `(50.3, 75.8)` est considérée comme étant sur la tuile `(50, 75)`.

### 4. Obstacles et obstructions

La carte gère les obstacles fixes (rochers, arbres, etc.). Lorsqu'un obstacle est chargé depuis un fichier `.map`, la tuile correspondante peut être marquée comme non-passable. Le moteur de jeu et l'IA peuvent alors interroger la carte pour savoir si un déplacement est valide.

### 5. L'élévation : un avantage tactique

L'élévation est une mécanique de combat essentielle.
- **Bonus d'attaque :** Si une unité attaque depuis une tuile plus élevée, ses dégâts sont augmentés de **25%**.
- **Malus d'attaque :** Si une unité attaque depuis une tuile plus basse, ses dégâts sont réduits de **25%** (dégâts x0.75).

Le moteur de jeu accède à l'élévation de l'attaquant et du défenseur via la carte avant de calculer les dégâts finaux.

### 6. Format des fichiers `.map`

Les cartes sont définies dans des fichiers texte simples avec une structure claire.

**Exemple de format :**
```
# Définit la taille de la grille (largeur x hauteur)
SIZE: 120 120

# Débute la définition de la grille d'élévation
GRID:
0 0 0 1 1 2 2 1 1 0 0 ... (120 valeurs par ligne)
0 0 1 2 3 4 3 2 1 0 0 ...
...
(120 lignes au total)
```
- **`SIZE` :** Définit les dimensions de la carte.
- **`GRID` :** Chaque ligne qui suit représente une rangée de tuiles, et chaque nombre correspond à l'élévation de cette tuile.

### 7. Extensibilité et intégration

La conception de la carte est modulaire et découplée de l'affichage.
- **Rendu ASCII et 2.5D :** La carte expose toutes les données nécessaires (élévation, unités, obstacles) pour qu'un moteur de rendu (terminal ou graphique) puisse afficher le champ de bataille. Elle ne gère pas l'affichage elle-même.
- **Minimap et snapshots HTML :** De la même manière, la carte fournit un accès complet à son état, permettant à des outils externes de générer une minimap ou un rapport de bataille détaillé.
- **Sauvegarde/Chargement :** Le format texte simple permet de sauvegarder et recharger des cartes facilement.



pour changer duréé chaque tour : dans fichier engine.py : LOGIC_SPEED_DIVIDER = ... (+ pour plus long)