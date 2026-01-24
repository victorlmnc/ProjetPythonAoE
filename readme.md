# MedievAIl - Battle GenerAIl Simulator 🏰⚔️

Bienvenue dans **MedievAIl**, un simulateur de batailles épiques en temps réel (RTS) où des Intelligences Artificielles s'affrontent !

## 🚀 Installation

Assurez-vous d'avoir Python 3.10+ et installez les dépendances :
```bash
pip install -r requirements.txt
```

---

## 🎮 Commandes Principales

L'interface en ligne de commande (CLI) permet de lancer tous les modes de jeu.

### 1. Partie Rapide (Mode Play)
Pour voir une bataille immédiate entre deux IAs par défaut :
```bash
python main.py play [OPTIONS]
```
**Options :**
- `-u <UnitType>` : Choisir le type d'unité (ex: `-u Knight`, `-u Pikeman`...).
- `-n <Nombre>` : Nombre d'unités par armée (défaut: 10).
- `-ai <Gen1> <Gen2>` : Choisir les généraux (ex: `-ai MajorDAFT ColonelKAISER`).
- `-t` : Mode Terminal (ASCII) au lieu de la vue 2.5D.
- `--map-size 60x60` : Taille de la carte.

### 2. Bataille Personnalisée (Mode Run)
Lancer un scénario spécifique (Fichier `.scen`, `.map` ou `.py`).
```bash
python main.py run <ScenarioFile> <AI1> <AI2> [-t]
```
**Exemple :**
```bash
python main.py run scenarios/compliance_test.scen MajorDAFT ColonelKAISER
```

### 3. Tournoi Automatique
Faites s'affronter plusieurs IAs sur plusieurs scénarios pour déterminer le meilleur général.
```bash
battle tourney [-G AI1 AI2 ...] [-S SCENARIO1 SCENARIO2 ...] [-N=10] [-na]
```
**Options :**
- `-G` : Généraux à combattre (défaut: tous les généraux disponibles).
- `-S` : Scénarios `.scen` ou `.map` (défaut: tous dans `scenarios/` et `maps/`).
- `-N` : Nombre de rounds par matchup (défaut: 10).
- `-na` : Désactiver l'alternance des positions (joueur 0/1).

**Exemple :**
```bash
python main.py tourney -G MajorDAFT ColonelKAISER -S maps/small.map -N 4
```
Le rapport HTML `tournament_report.html` contient :
- Score global par général (% victoires)
- Matrice Général vs Général
- Matchups détaillés par scénario
- Performance Général vs Scénario


### 4. Analyse Lanchester (Plot)
Testez la loi de Lanchester (N unités vs 2N unités) et générez un graphique de performance.
```bash
python main.py plot <AI> win_rate <Scenario> "<Range>"
```
**Exemple :**
```bash
python main.py plot MajorDAFT win_rate scenarios/1v1.map "range(10, 100, 10)"
```

---

## 🎮 Contrôles (Interface Graphique)

L'interface Pygame (Vue 2.5D) propose de nombreuses commandes pour naviguer et analyser la bataille.

| Action | Touche / Souris |
| :--- | :--- |
| **Déplacement Caméra** | **Flèches** ou **WASD** |
| **Panoramique (Drag)** | Maintenir **Clic Droit** et glisser |
| **Zoom** | **Molette Souris** (Haut/Bas) |
| **Pause / Reprendre** | **Espace** |
| **Accélérer / Ralentir** | **+** / **-** (Pavé Numérique) |
| **Afficher Infos Armées** | **F1** (ou **1**) |
| **Afficher Barres de Vie** | **F2** (ou **2**) |
| **Afficher Minimap** | **F3** (ou **3**) ou **M** |
| **Détails Unités** | **F4** (ou **4**) |
| **Sauvegarde Rapide** | **F11** |
| **Chargement Rapide** | **F12** |
| **Quitter** | **Échap** |

---

## 📝 Format de Scénario (.scen)

Le format unifié `.scen` permet de définir la carte, les unités et les bâtiments dans un seul fichier texte facile à éditer.

**Structure du fichier :**
```text
SIZE: <Largeur> <Hauteur>
GRID:
0 0 1 0 ... (Élévation par tuile)
...
UNITS:
<Type>, <X>, <Y>, <ID_Joueur>
...
STRUCTURES:
<Type>, <X>, <Y>, <ID_Joueur>
...
```

**Exemple :**
```text
SIZE: 60 60
UNITS:
Knight, 10.5, 10.5, 0
Pikeman, 12.0, 10.5, 0
Knight, 50.5, 50.5, 1
STRUCTURES:
Castle, 5.0, 5.0, 0
Wonder, 55.0, 55.0, 1
```
### 5. Entraînement IA (Mode Train)
Entraîner les agents via l'apprentissage par renforcement (Reinforcement Learning) sur une carte générée procéduralement.
```bash
python main.py train [OPTIONS]
```
**Options :**
- `--episodes <N>` : Nombre d'épisodes d'entraînement (défaut: 500).
- `--map-size <N>` : Taille de la carte pour l'entraînement (défaut: 80).
- `--units <N>` : Nombre d'unités par équipe pour l'entraînement (défaut: 40).

**Exemple:**
```bash
python main.py train --episodes 1000 --map-size 80 --units 40
```

### 6. Match de Démonstration (Mode Match)
Lancer un match de démonstration graphique (GUI) utilisant les modèles RL préalablement entraînés.
```bash
python main.py match [OPTIONS]
```
**Options :**
- `--map-size <N>` : Dimension de la carte (défaut: 120).
- `--units <N>` : Nombre d'unités par équipe (défaut: 50).
- `--maxturn <N>` : Limite de tours de jeu (-1 pour infini, défaut: 2000).

**Exemple :**
```bash
python main.py match --map-size 150 --units 100 --maxturn -1
```

### 7. Création de Contenu (Mode Create)
Générez facilement des cartes et des armées pour vos scénarios.
```bash
battle create <type> <filename> [OPTIONS]
```
**Options pour `map` :**
- `--width`, `--height` : Dimensions (défaut: 60x60).
- `--noise` : Facteur de bruit pour le terrain (0.0-1.0).

**Options pour `army` :**
- `--general` : IA à utiliser (défaut: MajorDAFT).
- `--units` : Liste et nombre d'unités (ex: "Knight:10,Pikeman:5").
- `--id` : ID de l'équipe (0 ou 1).

**Exemple :**
```bash
python main.py create map maps/new_map.map --width 80 --height 80
python main.py create army armies/my_army.txt --units "Knight:20,Archer:10"
```

---

## 🛠️ Outils de Développement

### Vérification de l'IA (Verify Kaiser)
Un script de test intensif pour vérifier la supériorité stratégique de ColonelKAISER.
```bash
python scripts/verify_kaiser.py
```

---

## 🏗️ Structure du Projet

- **`main.py`** : Point d'entrée principal (CLI).
- **`core/`** : Cœur de la simulation.
  - `engine.py` : Boucle principale et règles du jeu.
  - `map.py`, `unit.py`, `army.py` : Modèles de données.
- **`view/`** : Gestion de l'affichage.
  - `gui_view.py` : Vue isométrique Pygame avec zoom et caméra.
  - `terminal_view.py` : Vue ASCII pour le débogage.
- **`ai/`** : Intelligences Artificielles (Stratégies des généraux).
- **`scenarios/`** : Fichiers de définition des batailles (`.scen`, `.map`).
- **`assets/`** : Ressources graphiques (Sprites).
- **`utils/`** : Outils de chargement et de génération aléatoire.
