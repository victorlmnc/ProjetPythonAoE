# 🏰 MedievAIl - Battle GenerAIl Simulator

> Simulateur de batailles médiévales inspiré d'Age of Empires II, axé sur les tactiques IA.

---

## 🚀 Installation

1.  **Prérequis** : Python 3.10+
2.  **Installation** :
    ```bash
    pip install -r requirements.txt
    ```

---

## 🎮 Jouer Directement (Partie Rapide)

Le moyen le plus simple de lancer une bataille sans configuration complexe.

```bash
python main.py play
```
_Lance une bataille 10 vs 10 Chevaliers avec l'IA par défaut._

### Options Simples :
| Commande | Effet |
| :--- | :--- |
| `python main.py play -u Pikeman` | Jouer avec des **Piquiers** |
| `python main.py play -n 50` | **50 unités** par armée |
| `python main.py play -t` | Mode **Terminal** (sans fenêtre graphique) |
| `python main.py play -ai MajorDAFT ColonelKAISER` | Choisir les **IA** |

---

## ⌨️ Contrôles & Raccourcis (Interface Graphique)

Une fois le jeu lancé, voici comment interagir :

### 🕹️ Contrôles de Jeu
| Touche | Action |
| :---: | :--- |
| **Espace** | **Pause** / Reprendre |
| **Échap** | Quitter le jeu |
| **+ / -** | Accélérer / Ralentir le temps |
| **F11** | Sauvegarde Rapide |
| **F12** | Chargement Rapide |

### 🎥 Caméra
| Contrôle | Action |
| :---: | :--- |
| **Clic Droit + Glisser** | **Déplacer la carte** (Recommandé) |
| **Molette Souris** | **Zoom** Avant / Arrière |
| **Z / Q / S / D** | Déplacement Clavier (ou Flèches) |
| **Maj** + Direction | Déplacement Rapide |

### 📊 Affichage (Toggles)
Utilisez les touches numériques pour activer/désactiver les infos :

| Touche | Action |
| :---: | :--- |
| **1** | **Infos Armées** (Total unités, % vie...) |
| **2** | **Barres de Vie** (Au dessus des unités) |
| **3** | **Minimap** (En bas à droite) |
| **4** | **Détail Unités** (Liste des types restants) |

---

## ⚔️ Les Unités

Chaque unité a ses forces et faiblesses (Pierre-Papier-Ciseaux).

| Unité | HP | Atk | Spécial | Fort Contre... |
| :--- | :---: | :---: | :--- | :--- |
| **Knight** | 100 | 10 | Rapide | Archers, Infanterie légère |
| **Pikeman** | 55 | 4 | Bonus Cavalerie | **Chevaliers** (+22 dégâts) |
| **Crossbowman** | 35 | 6 | Portée (7.0) | Infanterie lente |
| **Onager** | 50 | 50 | Dégâts de Zone | Groupes d'unités |
| **EliteWarElephant** | 620 | 20 | Piétinement | Tout (mais lent) |
| **Monk** | 30 | 0 | Soin & Conversion | Unités isolées |

---

## 🧠 Les Généraux (IA)

| Nom | Comportement |
| :--- | :--- |
| `CaptainBRAINDEAD` | **Passif**. N'attaque que si touché. Sert de "Putsching Ball". |
| `MajorDAFT` | **Agressif Basique**. Fonce sur l'ennemi le plus proche. |
| `ColonelKAISER` | **Stratège**. Utilise des formations, le kiting et concentre ses tirs. |

---

## 🛠️ Création de Contenu

Plus besoin de modifier les fichiers à la main !

### 1. Créer une Carte Propre
```bash
python main.py create map maps/ma_carte.map --width 80 --height 80 --noise 0.2
```

### 2. Créer une Armée Personnalisée
```bash
# Exemple : Armée du Joueur 1 (ID 0) avec 20 Chevaliers et 10 Moines
python main.py create army armies/mon_armee.txt --general ColonelKAISER --units "Knight:20,Monk:10" --id 0
```

---

## 🔧 Commandes Avancées

Pour un contrôle total sur la simulation.

### 1. Lancer un Scénario Précis (`run`)
La commande ultime pour charger vos fichiers `.map` et `.txt`.

```bash
python main.py run <MAP> <IA1> <IA2> --army1 <FILE1> --army2 <FILE2> [options]
```

**Exemple Complet :**
```bash
python main.py run maps/ma_carte.map MajorDAFT ColonelKAISER --army1 armies/mon_armee.txt --army2 armies/ennemi.txt --max_turns 5000
```
> **Note :** Le nom de l'IA spécifié dans la commande est **prioritaire** sur celui écrit dans le fichier d'armée.

### 2. Tournoi Automatique (`tourney`)
Faire s'affronter des IA en boucle pour voir qui est la meilleure.

```bash
python main.py tourney -G MajorDAFT ColonelKAISER -S scenarios/test.map -N 100 --na
```
*   `-N 100` : 100 matchs.
*   `--na` : "No Animation" (Mode turbo sans graphismes).

### 3. Analyse de Données (`plot` / `lanchester`)
Vérifier l'équilibrage mathématique du jeu.

```bash
# Vérifier la loi de Lanchester (N vs 2N)
python main.py lanchester Knight 20 -t

# Générer un graphique de Win Rate
python main.py plot MajorDAFT win_rate scenarios/1v1.py "range(10, 100, 10)"
```

---

## 🧪 Développement

Pour lancer les tests unitaires et vérifier que tout fonctionne :

```bash
pytest tests/
```
---

##  M�caniques & R�gles

Quelques d�tails techniques sur le fonctionnement du jeu :

- **Formule de D�g�ts** : max(1, Attaque + Bonus - Armure)
- **�l�vation** : +25% de d�g�ts si l'attaquant est en hauteur.
- **Victoire** : Destruction totale de l'arm�e adverse.

---

##  V�rification de Conformit�

Pour v�rifier que le projet respecte chaque point du cahier des charges (Req 1 � 15), consultez le guide d�taill� :

 **[Voir le Guide de Test Complet (testing_guide.md)](testing_guide.md)**

