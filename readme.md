Noms IA dans fichiers de l armée mais aussi dans ligne de commande ?? fais quoi si diff ? qui decide entre les 2 ?
Tester la "meilleure" IA car elle fait nimp.
Charger les sprits et tester sur chaque unités et animations.
Toutes les images de chaque étapess de sprites mises sur github, pas bien ?


# 🏰 MedievAIl - Battle GenerAIl Simulator

> Simulateur de batailles médiévales inspiré d'Age of Empires II, axé sur les tactiques IA.

---

## 🚀 Installation

```bash
pip install pygame pillow matplotlib pytest
```

---

## 🎮 Lancer le Jeu

```bash
# Partie rapide (10v10 Knights, mode Pygame)
python main.py play

# Mode Terminal ASCII
python main.py play -t

# Personnaliser unités/nombre/IA
python main.py play -u Pikeman -n 20 -ai MajorDAFT ColonelKAISER
```

---

## ⌨️ Contrôles en Jeu (Pygame)

### Navigation Caméra

| Contrôle | Action |
|----------|--------|
| **W / ↑** | Haut |
| **A / ←** | Gauche |
| **S / ↓** | Bas |
| **D / →** | Droite |
| **Maj + WASD** | Déplacement rapide (3x) |
| **Clic droit + glisser** | Faire glisser la carte |
| **Molette** | Zoom avant / arrière |

### Affichage (Toggles)

| Touche | Action |
|--------|--------|
| **1** | Toggle infos armée |
| **2** | Toggle barres de vie |
| **3** ou **M** | Toggle minimap |
| **4** | Toggle détails unités |

### Contrôles Jeu

| Touche | Action |
|--------|--------|
| **Espace** | Pause / Reprendre |
| **F11** | Sauvegarde rapide |
| **F12** | Info chargement |
| **Échap** | Quitter |

---

## 🛠️ Génération Procédurale (Nouveau)

Plus besoin de créer les fichiers à la main ! Utilisez la commande `create`.

### 1. Créer une Carte
```bash
python main.py create map maps/ma_carte.map --width 80 --height 80 --noise 0.2
```

### 2. Créer une Armée
```bash
# Générer une armée avec 20 Chevaliers et 15 Piquiers
python main.py create army armies/mon_armee.txt --general MajorDAFT --units "Knight:20,Pikeman:15" --id 0
```

---

## � Référence Complète des Commandes

### 🌟 La Ligne de Commande Ultime (Mode Expert)
Pour définir **chaque aspect** de la bataille manuellement, utilisez `run` avec tous les paramètres :

```bash
python main.py run <MAP> <GENERAL_1> <GENERAL_2> --army1 <FICHIER_ARMEE_1> --army2 <FICHIER_ARMEE_2> --max_turns <TOURS> [-t] [-d <SAVE_FILE>]
```

**Exemple concret ultra-complet :**
```bash
python main.py run maps/terrain_accidenté.map ColonelKAISER MajorDAFT --army1 armies/ma_super_armee.txt --army2 armies/ennemi_base.txt --max_turns 5000

python main.py run maps/forest.map MajorDAFT MajorDAFT --army1 armies/armee_rouge.txt --army2 armies/armee_bleue.txt --max_turns 5000
```

| Paramètre | Description |
|-----------|-------------|
| `run` | Commande principale pour lancer un scénario précis. |
| `<MAP>` | Fichier map (`.map`) ou script scénario (`.py`). |
| `<GENERAL_1/2>` | IA des généraux (ex: `ColonelKAISER`, `MajorDAFT`, `CaptainBRAINDEAD`). |
| `--army1/2` | Chemins vers les fichiers de composition d'armée (requis si fichier `.map`). |
| `--max_turns` | Limite de tours avant fin forcée (défaut: 1000). |
| `-t` | (Optionnel) Force le mode **Terminal ASCII** (pas de fenêtre graphique). |
| `-d` | (Optionnel) Fichier de sauvegarde où enregistrer l'état final. |

> [!NOTE]
> **Priorité des Noms d'IA** : Si vous spécifiez un nom de général dans la ligne de commande (ex: `run ... MajorDAFT`), il sera **prioritaire** sur le nom défini dans le fichier d'armée (`GENERAL: ...`). Cela permet de tester différentes IA avec la même composition d'armée sans modifier le fichier.

---

### 🚀 Partie Rapide (`play`)
Le moyen le plus simple de lancer une bataille sans fichiers de config.

```bash
python main.py play -u Knight Pikeman -n 50 -ai ColonelKAISER CaptainBRAINDEAD
```

*   `-u`, `--units` : Types d'unités (ex: `Knight`, `Pikeman`, `Crossbowman`, `Monk`, `EliteWarElephant`).
*   `-n`, `--count` : Nombre d'unités **par type** pour chaque armée.
*   `-ai`, `--generals` : Les deux IA qui s'affrontent.

---

### 🏆 Tournoi Automatique (`tourney`)
Faire s'affronter plusieurs IA sur plusieurs cartes en boucle.

```bash
python main.py tourney -G MajorDAFT ColonelKAISER -S maps/small.map maps/large.map -N 10 --na
```

*   `-G` : Liste des Généraux participants.
*   `-S` : Liste des cartes/scénarios à jouer.
*   `-N` : Nombre de rounds par match-up.
*   `--na` : "No Animation" (mode super-rapide sans rendu graphique).

---

### 📊 Analyse & Graphiques (`plot` & `lanchester`)
Pour vérifier l'équilibrage et la loi de Lanchester.

```bash
# Vérifier la loi carrée de Lanchester (N vs 2N)
python main.py lanchester Knight 20 -t

# Générer un graphique de performance (nécessite matplotlib)
python main.py plot MajorDAFT win_rate scenarios/1v1.py "range(10, 100, 10)" --opponent CaptainBRAINDEAD
```

---

## 👥 Généraux (IA)

| Nom | Comportement |
|-----|--------------|
| `CaptainBRAINDEAD` | Passif, n'attaque que si agressé |
| `MajorDAFT` | Agressif, attaque l'ennemi le plus proche |
| `ColonelKAISER` | Avancé : formations, kiting, focus fire |

---

## ⚔️ Unités

| Unité | HP | Attaque | Portée | Spécial |
|-------|-----|---------|--------|---------|
| Knight | 100 | 10 | 0.5 | - |
| Pikeman | 55 | 4 | 0.5 | +22 vs Cavalerie |
| Crossbowman | 35 | 6 | 7.0 | - |
| Onager | 50 | 50 | 8.0 | Splash damage |
| EliteWarElephant | 620 | 20 | 0.5 | Trample damage |
| Monk | 30 | 0 | 9.0 | Heal & Convert |

---

## 🧪 Tests

```bash
pytest tests/test_unit.py -v
```

---

## ⚡ Mécaniques

- **Formule dégâts** : `max(1, Attaque + Bonus - Armure)`
- **Élévation** : +25% dégâts depuis hauteur
- **Victoire** : Destruction armée ou Wonder ennemie

---

## 📜 Vérification de Conformité (PDF)

Pour vérifier que le projet respecte chaque point du cahier des charges (Req 1 à 15), consultez le guide détaillé :

👉 **[Voir le Guide de Test complet (testing_guide.md)](testing_guide.md)**

### Résumé des vérifications clés :
1.  **Sprites** : Lancez `python main.py play` et zoomez.
2.  **Scénarios Python** : Lancez `python main.py run scenarios/test_scenario.py MajorDAFT MajorDAFT`.
3.  **Vitesse** : Appuyez sur `+` ou `-` en jeu.
4.  **Lanchester** : Lancez `python main.py lanchester Knight 50 -t`.
5.  **Tournoi** : Lancez `python main.py tourney -G MajorDAFT CaptainBRAINDEAD -S scenarios/test_scenario.py`.
