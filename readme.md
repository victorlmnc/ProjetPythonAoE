# Medieval Battle Simulator

Simulateur de batailles en temps reel (RTS) avec differentes strategies, développé en Python.

## Installation

Assurez-vous d'avoir Python 3.10+ et installez les dépendances :
```bash
pip install -r requirements.txt
```

---

## Guide des Commandes CLI

L'interface en ligne de commande (CLI) permet de lancer tous les modes de jeu via `python main.py`.

### 1. Partie Rapide (Play)
Lancer une bataille rapide entre deux généraux.
```bash
python main.py play (+ [OPTIONS] si voulu)
```
**Options :**
- `-u <UnitType>` : Choisir le type d'unité (ex: `-u Knight`, `-u Pikeman`...); (défaut: Knight).
- `-n <Nombre>` : Nombre d'unités par armée (défaut: 10).
- `-ai <Gen1> <Gen2>` : Choisir les généraux (ex: `-ai MajorDAFT ColonelKAISER`); (défaut: MajorDAFT vs MajorDAFT).
- `-t` : Mode Terminal (ASCII) au lieu de la vue 2.5D (défaut: vue 2.5D).
- `--map-size 60x60` : Taille de la carte (défaut: 120x120).

**Exemple complet avec options :**
```bash
python main.py play -u Knight Pikeman Crossbowman -n 50 -ai MajorDAFT ColonelKAISER --map-size 80x80
```



### 2. Lancer un Scénario (Run)
Exécuter un scénario spécifique depuis un fichier `.scen`, `.map` ou `.py` (Pour créer un scénario, voir la section "Détails Techniques").
```bash
python main.py run <ScenarioFile> <AI1> <AI2> [-t]
```
**Exemple :**
```bash
python main.py run scenarios/mega_battle.scen MajorDAFT ColonelKAISER
```



### 3. Tournoi Automatique (Tourney)
Faire s'affronter plusieurs généraux sur plusieurs scénarios et générer un rapport HTML.
```bash
python main.py tourney [-G AI1 AI2 ...] [-S SCENARIO1 SCENARIO2 ...] [-N=10] [-na]
```
**Options :**
- `-G` : Généraux à combattre (défaut: tous disponibles).
- `-S` : Scénarios `.scen` ou `.map` (défaut: tous dans `scenarios/` et `maps/`).
- `-N` : Nombre de rounds par matchup (défaut: 10).
- `-na` : Désactiver l'alternance des positions (joueur 0/1).

**Exemple :**
```bash
python main.py tourney -G MajorDAFT ColonelKAISER -S scenarios/tourney_battle.scen -N 4
```



### 4. Scénario Lanchester (Lanchester)
Tester la loi de Lanchester (N unités vs 2N unités).
Visualisez la bataille en temps réel et obtenez automatiquement un graphique des pertes en fin de partie.

```bash
python main.py lanchester <UnitType> <N> [-t]
```
**Exemple :**
```bash
python main.py lanchester Knight 50
```
(Génère automatiquementle fichier `lanchester_run_knight.png`)



### 5. Graphiques de Performance (Plot)
Générer un graphique de performance (win rate, dégâts...) en fonction d'une variable.
```bash
python main.py plot <AI> <plotter> <Scenario> "<Range>"
```
**Arguments :**
- `<plotter>` : Type de graphique (`win_rate`, `damage`, `survival`).
- `<Range>` : Variation (ex: `range(10, 100, 10)`).

**Exemple :**
```bash
python main.py plot MajorDAFT win_rate scenarios/exemple.map "range(10, 100, 10)"
```



### 6. Entrainement RL (Train)
Entraîner les agents avec l'apprentissage par renforcement.
```bash
python main.py train [OPTIONS]
```
**Options :**
- `--episodes <N>` : Nombre d'épisodes (défaut: 500).
- `--map-size <N>` : Taille de la carte (défaut: 80).
- `--units <N>` : Nombre d'unités (défaut: 40).



### 7. Match de Démonstration pour RL (Match)
Lancer un match graphique pré-configuré.
```bash
python main.py match [OPTIONS]
```
**Options :**
- `--map-size <N>` : Dimension (défaut: 120).
- `--units <N>` : Unités par équipe (défaut: 50).
- `--maxturn <N>` : Limite de tours (-1 pour infini).
**Exemple :**
```bash
python python main.py match --map-size 120 --units 40 --maxturn -1
```



### 8. Création de Contenu (Create)
Générer des cartes et des armées pour vos scénarios.
```bash
python main.py create <type> <filename> [OPTIONS]
```
**Créer une carte :**
```bash
python main.py create map maps/new_map.map --width 80 --height 80 --noise 0.1
```
**Créer une armée :**
```bash
python main.py create army armies/my_army.txt --units "Knight:20,Archer:10"
```

---

## Contrôles (Interface Graphique)

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

## Détails Techniques

### Création de Scénarios Personnalisés (.scen)

Pour créer votre propre scénario :
1. Créez un nouveau fichier texte avec l'extension `.scen` (ex: `mon_scenario.scen`).
2. Ouvrez-le avec un éditeur de texte (Notepad, VS Code...).
3. Respectez le format suivant :

```text
SIZE: <Largeur> <Hauteur>
UNITS:
<Type>, <X>, <Y>, <ID_Joueur>
...
STRUCTURES:
<Type>, <X>, <Y>, <ID_Joueur>
...
```

**Unités disponibles :**
`Knight`, `Pikeman`, `Crossbowman`.

**Bâtiments disponibles :**
`Castle`, `Wonder`.

**ID Joueur :**
- `0` : Armée 1 (Bleu / Haut-Gauche)
- `1` : Armée 2 (Rouge / Bas-Droite)

**Exemple Complet (copier-coller dans un fichier .scen) :**
```text
SIZE: 80 80
UNITS:
Knight, 10, 10, 0
Pikeman, 12, 10, 0
Archer, 15, 15, 0
Knight, 70, 70, 1
Pikeman, 68, 70, 1
STRUCTURES:
Castle, 5, 5, 0
Wonder, 75, 75, 1
```

## Architecture du Projet

- **`main.py`** : Point d'entrée principal (CLI).
- **`core/`** : Moteur de jeu (`engine.py`), modèles (`unit.py`, `map.py`).
- **`view/`** : Système de rendu (`gui_view.py`, `terminal_view.py`).
- **`ai/`** : Logique des agents et stratégies.
- **`scenarios/`** : Fichiers de configuration de batailles.
- **`assets/`** : Sprites et ressources graphiques.
- **`utils/`** : Générateurs et utilitaires.



**Pour les détails de la vue terminal, voir le fichier TERMINAL_VIEW_README.md**